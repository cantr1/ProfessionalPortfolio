MQTT Project: Terminal Chat Between Two Hosts
🧠 Concept:

Two devices (VMs/containers) communicate via an MQTT broker using the publish/subscribe model — like a command-line chat room.

✅ Step 1: Install Mosquitto on One VM (Broker)

# On the broker VM
```
sudo apt update
sudo apt install mosquitto mosquitto-clients
sudo systemctl enable --now mosquitto
```

Allow port 1883 through the firewall if needed.

Open /etc/mosquitto/mosquitto.conf
Add the following lines:
```
listener 1883
allow_anonymous true
```

✅ Step 2: Test the Broker Locally
# Terminal 1: Subscribe
mosquitto_sub -h localhost -t "chat/room1"

# Terminal 2: Publish
mosquitto_pub -h localhost -t "chat/room1" -m "Hello, World!"

✅ Step 3: Set Up the Second VM/Container as a Client
On the second VM/container:
`sudo apt install mosquitto-clients -y`

Test connection to the broker:

# Replace <broker_ip> with the actual IP of the broker VM
`mosquitto_sub -h <broker_ip> -t "chat/room1"`

From the broker VM:
`mosquitto_pub -h localhost -t "chat/room1" -m "Hello from the broker!"`

✅ Step 4: Create Python Chat Clients

Install paho-mqtt on both systems:

`sudo apt install python3-paho-mqtt`

Basic Subscriber Script (chat_sub.py):

import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    print(f"\n[{msg.topic}] {msg.payload.decode()}")

client = mqtt.Client()
client.on_message = on_message
client.connect("BROKER_IP")
client.subscribe("chat/room1")
client.loop_forever()

Basic Publisher Script (chat_pub.py):

import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("BROKER_IP")

while True:
    message = input("You: ")
    client.publish("chat/room1", message)

Run chat_sub.py on one VM, and chat_pub.py on the other.