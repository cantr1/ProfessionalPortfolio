import paho.mqtt.client as mqtt
from gpiozero import LED
from time import sleep

led = LED(17)

def on_message(client, userdata, msg):
    payload = msg.payload.decode().strip().upper()
    print(f"[{msg.topic}] {payload}")

    if payload == 'ON':
        led.on()
        print("LED turned ON")
    elif payload == 'OFF':
        led.off()
        print("LED turned OFF")
    elif payload == 'BLINK':
        for _ in range(10):
            led.on()
            sleep(0.2)
            led.off()
            sleep(0.2)
    else:
        print("Unrecognized command.")

client = mqtt.Client()
client.on_message = on_message
client.connect("192.168.1.103")
client.subscribe("led")
client.loop_forever()
