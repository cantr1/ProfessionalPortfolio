import paho.mqtt.client as mqtt
import json

def publish_blockchain(block, broker="localhost", port=1883, topic="blockchain/data"):
    client = mqtt.Client()
    client.connect(broker, port)
    payload = json.dumps(block)
    client.publish(topic, payload)
    client.disconnect()
