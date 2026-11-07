#!/usr/bin/env python3
"""Check MQTT traffic in both directions between TCP and WebSocket clients.

Run with the project's environment: mqttenv/bin/python mqtt_websocket_check.py
Uses temporary, non-retained test topics; it does not operate the hardware.
"""

import sys
import threading
import uuid

import paho.mqtt.client as mqtt


class Probe:
    def __init__(self, transport, port, topic, expected):
        self.port = port
        self.topic = topic
        self.expected = expected.encode("utf-8")
        self.ready = threading.Event()
        self.received = threading.Event()
        self.error = None
        # The project uses Paho's version 1 callbacks (Paho 1.x and 2.x).
        self.client = mqtt.Client(
            client_id="house-check-" + uuid.uuid4().hex[:12],
            protocol=mqtt.MQTTv311,
            transport=transport,
        )
        if transport == "websockets":
            self.client.ws_set_options(path="/")  # Same path as the Chromebook app.
        self.client.on_connect = self.on_connect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc != 0:
            self.error = "MQTT connection refused: " + str(rc)
            self.ready.set()
            return
        result, _ = client.subscribe(self.topic, qos=0)
        if result != mqtt.MQTT_ERR_SUCCESS:
            self.error = "Subscription request failed: " + str(result)
            self.ready.set()

    def on_subscribe(self, client, userdata, mid, granted_qos):
        if not granted_qos or any(qos == 128 for qos in granted_qos):
            self.error = "Broker rejected test subscription"
        self.ready.set()

    def on_message(self, client, userdata, message):
        if message.topic == self.topic and message.payload == self.expected:
            self.received.set()

    def start(self):
        self.client.connect("127.0.0.1", self.port, keepalive=15)
        self.client.loop_start()
        if not self.ready.wait(5):
            raise RuntimeError("Timed out waiting for subscription on port " + str(self.port))
        if self.error:
            raise RuntimeError(self.error)

    def stop(self):
        self.client.disconnect()
        self.client.loop_stop()


def main():
    base = "simpsons-house/setup-check/" + uuid.uuid4().hex
    tcp = Probe("tcp", 1883, base + "/to-tcp", "from-websocket")
    websocket = Probe("websockets", 9001, base + "/to-websocket", "from-tcp")
    try:
        tcp.start()
        websocket.start()
        if tcp.client.publish(websocket.topic, "from-tcp", qos=0).rc != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError("TCP publish failed")
        if websocket.client.publish(tcp.topic, "from-websocket", qos=0).rc != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError("WebSocket publish failed")
        if not websocket.received.wait(5):
            raise RuntimeError("WebSocket client did not receive the TCP message")
        if not tcp.received.wait(5):
            raise RuntimeError("TCP client did not receive the WebSocket message")
        print("MQTT TCP and WebSocket publish/subscribe test passed in both directions.")
        return 0
    except (OSError, RuntimeError, ValueError) as error:
        print("MQTT TCP/WebSocket test failed: " + str(error), file=sys.stderr)
        return 1
    finally:
        websocket.stop()
        tcp.stop()


if __name__ == "__main__":
    sys.exit(main())
