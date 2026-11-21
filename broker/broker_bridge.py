# -*- coding: utf-8 -*-
"""
MQTT Broker Bridge Module.
Provides dual-mode MQTT connectivity:
1. Simulated In-Memory Broker (default: zero-dependency, thread-safe, 100% offline reproducible)
2. Live Paho-MQTT Client (connects to local Eclipse Mosquitto or public cloud brokers)
"""
import sys
import os
import json
import time
import queue
import threading
from typing import Callable, Dict, List, Any

# Ensure project root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

try:
    import paho.mqtt.client as mqtt
    PAHO_AVAILABLE = True
except ImportError:
    PAHO_AVAILABLE = False


class SimulatedBroker:
    """
    Thread-safe in-memory publish/subscribe broker for offline prototype execution.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SimulatedBroker, cls).__new__(cls)
                cls._instance.subscribers: Dict[str, List[Callable]] = {}
                cls._instance.queue = queue.Queue()
                cls._instance.running = True
                cls._instance.worker = threading.Thread(
                    target=cls._instance._dispatch_loop, daemon=True
                )
                cls._instance.worker.start()
            return cls._instance

    def _dispatch_loop(self):
        while self.running:
            try:
                topic, payload_str = self.queue.get(timeout=0.1)
                with self._lock:
                    handlers = list(self.subscribers.get(topic, []))
                for handler in handlers:
                    try:
                        handler(topic, payload_str)
                    except Exception as e:
                        print(f"[SimulatedBroker Error] Handler exception: {e}")
                self.queue.task_done()
            except queue.Empty:
                continue

    def publish(self, topic: str, payload_str: str):
        self.queue.put((topic, payload_str))

    def subscribe(self, topic: str, callback: Callable[[str, str], None]):
        with self._lock:
            if topic not in self.subscribers:
                self.subscribers[topic] = []
            self.subscribers[topic].append(callback)

    def unsubscribe(self, topic: str, callback: Callable[[str, str], None]):
        with self._lock:
            if topic in self.subscribers and callback in self.subscribers[topic]:
                self.subscribers[topic].remove(callback)

    @classmethod
    def reset_for_testing(cls):
        """Clear all subscriptions. ONLY for use in automated tests."""
        with cls._lock:
            if cls._instance is not None:
                cls._instance.subscribers.clear()


class BaseMQTTClient:
    """Unified interface for both simulated and live MQTT clients."""
    def connect(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    def publish(self, topic: str, payload: str):
        raise NotImplementedError

    def subscribe(self, topic: str, callback: Callable[[str, str], None]):
        raise NotImplementedError


class LocalSimulatedClient(BaseMQTTClient):
    """Client that communicates via the in-memory SimulatedBroker."""
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.broker = SimulatedBroker()
        self.connected = False
        self._subscriptions: List[tuple] = []

    def connect(self):
        self.connected = True
        return True

    def disconnect(self):
        self.connected = False
        for topic, callback in self._subscriptions:
            self.broker.unsubscribe(topic, callback)
        self._subscriptions.clear()

    def publish(self, topic: str, payload: str):
        if not self.connected:
            raise ConnectionError("Client is not connected.")
        self.broker.publish(topic, payload)

    def subscribe(self, topic: str, callback: Callable[[str, str], None]):
        if not self.connected:
            raise ConnectionError("Client is not connected.")
        self.broker.subscribe(topic, callback)
        self._subscriptions.append((topic, callback))


class PahoLiveClient(BaseMQTTClient):
    """Client that communicates with a real MQTT broker via paho-mqtt."""
    def __init__(self, client_id: str):
        if not PAHO_AVAILABLE:
            raise RuntimeError("paho-mqtt is not installed.")
        self.client_id = client_id
        # Support Paho MQTT v2 CallbackAPIVersion
        try:
            self.client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2, client_id=client_id
            )
        except AttributeError:
            self.client = mqtt.Client(client_id=client_id)
        self.callbacks: Dict[str, Callable] = {}
        self.client.on_message = self._on_message

    def _on_message(self, client, userdata, message):
        payload_str = message.payload.decode("utf-8")
        topic = message.topic
        if topic in self.callbacks:
            self.callbacks[topic](topic, payload_str)

    def connect(self):
        self.client.connect(
            config.MQTT_BROKER_HOST, config.MQTT_BROKER_PORT, config.MQTT_KEEPALIVE
        )
        self.client.loop_start()

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    def publish(self, topic: str, payload: str):
        self.client.publish(topic, payload)

    def subscribe(self, topic: str, callback: Callable[[str, str], None]):
        self.callbacks[topic] = callback
        self.client.subscribe(topic)


def get_mqtt_client(client_id: str) -> BaseMQTTClient:
    """Factory function returning the configured MQTT client implementation."""
    if config.USE_SIMULATED_BROKER:
        return LocalSimulatedClient(client_id)
    else:
        return PahoLiveClient(client_id)

