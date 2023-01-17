import os
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))


def init():
    global client
    print("Connecting MQTT")
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect(os.environ["MQTT_SERVER"],
                   int(os.environ["MQTT_PORT"]), int(os.environ["MQTT_KEEPALIVE"]))


def publish(topic, payload):
    client.publish(topic, payload)
