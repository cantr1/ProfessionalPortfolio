import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    print(f"\n[{msg.topic}] {msg.payload.decode()}")

client = mqtt.Client()
client.on_message = on_message
client.connect("BROKER_IP")
client.subscribe("chat/room1")
client.loop_forever()