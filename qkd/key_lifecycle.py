# -*- coding: utf-8 -*-
"""
QKD Key Lifecycle State Machine.

Implements deterministic key lifecycle management for BB84-derived AES-256-GCM sessions.

States:
  UNINITIALIZED  -> No key has been established yet.
  KEY_ESTABLISHED-> BB84 negotiation just completed; key installed but publishing not yet started.
  ACTIVE         -> Encrypting telemetry; invocation counter rising.
  REKEY_REQUIRED -> Counter reached threshold; new BB84 session must run before next publish.
  REKEYING       -> New BB84 negotiation in flight; publisher paused; pending queue draining.
  ACTIVE_NEW_KEY -> New key installed; publishing resumed under new key ID.
  KEY_EXPIRED    -> Key exhausted without successful rekey; publishing blocked.
  SECURITY_ABORT -> QBER threshold exceeded during rekey attempt; session terminated.

NOTE:
  This is a software simulation of key lifecycle management.
  It does NOT constitute an information-theoretically secure key management channel.
  The receiver learns the new key via the same in-process shared-state channel used by
  the simulated broker transport — which is not a cryptographically authenticated
  secure out-of-band channel in this prototype.
"""
import logging
import os
import threading
import time
import uuid
from enum import Enum, auto
from typing import Callable, Optional, Dict, Any

logger = logging.getLogger(__name__)


class KeyState(str, Enum):
    """Explicit states in the key lifecycle state machine."""
    UNINITIALIZED   = "UNINITIALIZED"
    KEY_ESTABLISHED = "KEY_ESTABLISHED"
    ACTIVE          = "ACTIVE"
    REKEY_REQUIRED  = "REKEY_REQUIRED"
    REKEYING        = "REKEYING"
    ACTIVE_NEW_KEY  = "ACTIVE_NEW_KEY"
    KEY_EXPIRED     = "KEY_EXPIRED"
    SECURITY_ABORT  = "SECURITY_ABORT"


class KeyExpirationError(Exception):
    """Raised when an attempt is made to encrypt under an expired or retired key."""


class RekeyFailedError(Exception):
    """Raised when a BB84 renegotiation attempt fails and the session cannot recover."""


class KeyLifecycleManager:
    """
    Thread-safe finite state machine that enforces invocation limits and
    orchestrates BB84 renegotiation when the active key approaches expiry.

    Parameters
    ----------
    bb84_factory : Callable[[], tuple[bytes, dict]]
        Callable that runs a fresh BB84 session and returns
        (new_aes_key_bytes, session_metadata_dict).
        On failure it must raise an exception or return (None, metadata).
    on_key_rotated : Callable[[str, bytes, dict], None]
        Invoked when a new key becomes active.
        Arguments: (new_key_id, new_key_bytes, session_metadata).
    max_invocations : int
        Maximum number of encryption operations permitted per key.
        Default matches NIST SP 800-38D guidance for a 96-bit random nonce.
        Set to a small value (e.g., 5) during integration testing.
    db_logger : optional callable
        log_key_lifecycle_event(event_dict) called for every state transition.
    """

    def __init__(
        self,
        bb84_factory: Callable,
        on_key_rotated: Callable,
        max_invocations: int = 100_000,
        db_logger: Optional[Callable[[Dict[str, Any]], None]] = None,
        experiment_id: Optional[str] = None,
    ):
        self._bb84_factory = bb84_factory
        self._on_key_rotated = on_key_rotated
        self._max_invocations = max_invocations
        self._db_logger = db_logger
        self.experiment_id = experiment_id

        self._lock = threading.Lock()
        self._rekey_complete = threading.Event()

        self.state: KeyState = KeyState.UNINITIALIZED
        self.key_id: Optional[str] = None
        self.aes_key: Optional[bytes] = None
        self.invocation_count: int = 0
        self.retired_key_ids: set = set()

        # Structured lifecycle event log (in-memory; also persisted via db_logger)
        self.lifecycle_events: list = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def install_initial_key(self, key_bytes: bytes, session_meta: Dict[str, Any]) -> str:
        """
        Install the first BB84-derived key.  Must be called before the first publish.

        Returns the new key_id.
        """
        with self._lock:
            if self.state not in (KeyState.UNINITIALIZED,):
                raise RuntimeError(
                    f"install_initial_key called in invalid state {self.state}"
                )
            key_id = self._generate_key_id()
            self._install_key_locked(key_id, key_bytes, session_meta, "INITIAL_INSTALL")
            self.state = KeyState.KEY_ESTABLISHED
            return key_id

    def pre_encrypt_check(self) -> bytes:
        """
        Called by the sensor client before every encryption operation.

        Returns the current AES key if the state machine permits encryption.
        Triggers synchronous rekeying if the threshold has been reached.

        Raises
        ------
        KeyExpirationError
            If the key is expired or the state machine is in SECURITY_ABORT.
        RekeyFailedError
            If rekeying was attempted and failed.
        """
        with self._lock:
            state = self.state

        if state in (KeyState.KEY_EXPIRED, KeyState.SECURITY_ABORT):
            raise KeyExpirationError(
                f"Encryption blocked: key lifecycle is in terminal state {state}."
            )

        if state == KeyState.REKEY_REQUIRED:
            # Trigger synchronous rekeying; blocks until complete or raises
            self._do_rekey()

        if state == KeyState.REKEYING:
            # Another thread is rekeying; wait for completion
            if not self._rekey_complete.wait(timeout=120.0):
                raise RekeyFailedError("Timed out waiting for rekeying to complete.")

        with self._lock:
            if self.state in (KeyState.KEY_EXPIRED, KeyState.SECURITY_ABORT):
                raise KeyExpirationError(
                    f"Encryption blocked after rekey failure: state={self.state}."
                )
            if self.aes_key is None:
                raise KeyExpirationError("No active key available for encryption.")

            self.invocation_count += 1
            count = self.invocation_count
            key = self.aes_key
            # Transition ACTIVE_NEW_KEY -> ACTIVE once first post-rekey frame is sent
            if self.state == KeyState.ACTIVE_NEW_KEY:
                self.state = KeyState.ACTIVE
            # Check whether threshold has been crossed
            if count >= self._max_invocations:
                self.state = KeyState.REKEY_REQUIRED
                self._emit_event("REKEY_THRESHOLD_REACHED", {
                    "invocation_count": count,
                    "threshold": self._max_invocations,
                    "key_id": self.key_id,
                })

        return key

    def mark_active(self):
        """Transition KEY_ESTABLISHED -> ACTIVE on first successful publish."""
        with self._lock:
            if self.state == KeyState.KEY_ESTABLISHED:
                self.state = KeyState.ACTIVE

    # ------------------------------------------------------------------
    # Internal rekeying machinery
    # ------------------------------------------------------------------

    def _do_rekey(self):
        """
        Execute a BB84 renegotiation synchronously.
        Must NOT be called while holding self._lock.
        """
        with self._lock:
            if self.state == KeyState.REKEYING:
                # Another thread already started; wait for it
                return
            self.state = KeyState.REKEYING
            old_key_id = self.key_id
            old_invocations = self.invocation_count
            self._rekey_complete.clear()

        rekey_start = time.perf_counter()
        self._emit_event("REKEY_STARTED", {
            "old_key_id": old_key_id,
            "invocation_count": old_invocations,
            "threshold": self._max_invocations,
        })
        logger.info(
            "[KeyLifecycle] Rekeying initiated. Old key_id=%s, invocations=%d/%d",
            old_key_id, old_invocations, self._max_invocations,
        )

        try:
            new_key_bytes, session_meta = self._bb84_factory()
        except Exception as exc:
            rekey_duration = (time.perf_counter() - rekey_start) * 1000.0
            with self._lock:
                self.state = KeyState.SECURITY_ABORT
                self._retire_key_locked(old_key_id)
                self.aes_key = None
                self._rekey_complete.set()
            self._emit_event("REKEY_FAILED", {
                "old_key_id": old_key_id,
                "reason": str(exc),
                "duration_ms": rekey_duration,
            })
            logger.error("[KeyLifecycle] Rekeying FAILED: %s", exc)
            raise RekeyFailedError(f"BB84 renegotiation failed: {exc}") from exc

        if new_key_bytes is None:
            # BB84 aborted cleanly (e.g. QBER threshold exceeded)
            rekey_duration = (time.perf_counter() - rekey_start) * 1000.0
            with self._lock:
                self.state = KeyState.SECURITY_ABORT
                self._retire_key_locked(old_key_id)
                self.aes_key = None
                self._rekey_complete.set()
            self._emit_event("REKEY_SECURITY_ABORT", {
                "old_key_id": old_key_id,
                "qber": session_meta.get("qber"),
                "duration_ms": rekey_duration,
            })
            logger.error(
                "[KeyLifecycle] SECURITY ABORT — BB84 rekey returned no key "
                "(QBER=%.4f exceeds threshold).",
                session_meta.get("qber", -1.0),
            )
            raise RekeyFailedError(
                "BB84 session aborted: QBER threshold exceeded during renegotiation."
            )

        rekey_duration = (time.perf_counter() - rekey_start) * 1000.0

        with self._lock:
            self._retire_key_locked(old_key_id)
            new_key_id = self._generate_key_id()
            self._install_key_locked(new_key_id, new_key_bytes, session_meta, "REKEY_INSTALL")
            self.state = KeyState.ACTIVE_NEW_KEY

        self._emit_event("REKEY_COMPLETED", {
            "old_key_id": old_key_id,
            "new_key_id": new_key_id,
            "duration_ms": rekey_duration,
            "pa_output_bits": session_meta.get("pa_output_bits"),
            "qber": session_meta.get("qber"),
            "reconciled_bits": session_meta.get("reconciled_bits"),
        })
        logger.info(
            "[KeyLifecycle] Rekeying COMPLETED. New key_id=%s, duration=%.1f ms",
            new_key_id, rekey_duration,
        )

        # Notify the receiver BEFORE releasing rekey_complete, so the receiver
        # holds the new key before any publisher thread resumes.
        try:
            self._on_key_rotated(new_key_id, new_key_bytes, session_meta)
        except Exception as exc:
            logger.error("[KeyLifecycle] on_key_rotated callback raised: %s", exc)

        # Release the gate: waiting publisher threads may now proceed
        self._rekey_complete.set()

    # ------------------------------------------------------------------
    # Private helpers (all call assumes _lock is held or not needed)
    # ------------------------------------------------------------------

    def _install_key_locked(
        self, key_id: str, key_bytes: bytes, session_meta: Dict[str, Any], reason: str
    ):
        """Install a new key; resets invocation counter.  Caller must hold self._lock."""
        self.key_id = key_id
        self.aes_key = key_bytes
        self.invocation_count = 0
        self._emit_event(reason, {
            "key_id": key_id,
            "pa_output_bits": session_meta.get("pa_output_bits"),
            "qber": session_meta.get("qber"),
            "max_invocations": self._max_invocations,
        })

    def _retire_key_locked(self, key_id: Optional[str]):
        """Mark old key as retired; nullify active material.  Caller holds self._lock."""
        if key_id:
            self.retired_key_ids.add(key_id)
        self.aes_key = None   # Defensive: wipe from memory immediately

    @staticmethod
    def _generate_key_id() -> str:
        return "KID-" + uuid.uuid4().hex[:12].upper()

    def _emit_event(self, event_type: str, details: Dict[str, Any]):
        """
        Emit a structured lifecycle event.
        NEVER logs raw key material, nonces, or plaintext.
        """
        event = {
            "event_type": event_type,
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "state": self.state.value if hasattr(self.state, 'value') else str(self.state),
            "experiment_id": self.experiment_id,
            **details,
        }
        self.lifecycle_events.append(event)
        if self._db_logger:
            try:
                self._db_logger(event)
            except Exception as exc:
                logger.warning("[KeyLifecycle] DB logger raised: %s", exc)

    # ------------------------------------------------------------------
    # Diagnostic read-only properties
    # ------------------------------------------------------------------

    @property
    def current_key_id(self) -> Optional[str]:
        with self._lock:
            return self.key_id

    @property
    def current_invocation_count(self) -> int:
        with self._lock:
            return self.invocation_count

    @property
    def current_state(self) -> KeyState:
        with self._lock:
            return self.state

    def is_retired(self, key_id: str) -> bool:
        with self._lock:
            return key_id in self.retired_key_ids
