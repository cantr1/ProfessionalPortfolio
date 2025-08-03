import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("BROKER_IP")  # Replace with actual broker IP

while True:
    message = input("You: ")
    client.publish("chat/room1", message)