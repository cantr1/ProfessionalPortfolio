import paho.mqtt.client as mqtt
from gpiozero import LED
from time import sleep
import string

led = LED(17)

def on_message(client, userdata, msg):
    payload = msg.payload.decode.strip().lower()
    translator = str.maketrans('', '', string.punctuation)
    processed_payload = payload.translate(translator)

    print(processed_payload)

client = mqtt.Client()
client.on_message = on_message
client.connect("BROKER IP")
client.subscribe("morse")
client.loop_forever()
