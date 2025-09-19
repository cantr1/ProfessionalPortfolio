# Used to create a container image -> docker build -t mqtt_blockchain:1.0 .
# After building the image, use the following to start:
# docker run --name blockchain_broker -p 1883:1883 mqtt_blockchain:1.0 
FROM eclipse-mosquitto

COPY mosquitto.conf /mosquitto/config/mosquitto.conf

EXPOSE 1883
