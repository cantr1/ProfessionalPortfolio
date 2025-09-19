import paho.mqtt.client as mqtt
from resources import exit_message
import json

def on_message(client, userdata, msg):
    blockchain = json.loads(msg.payload.decode())
    print("📡 Received blockchain update:")
    print(json.dumps(blockchain, indent=4, sort_keys=True))


def subscribe_blockchain(broker="localhost", port=1883, topic="blockchain/data"):
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(broker, port)
    client.subscribe(topic)
    client.loop_forever()

def main() -> None:
    try:
        subscribe_blockchain()
    except KeyboardInterrupt:
        print(exit_message)



if __name__ == "__main__":
    main()