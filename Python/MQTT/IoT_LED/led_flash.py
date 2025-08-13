#!/usr/bin/env python3
from gpiozero import LED
from time import sleep

led = LED(17)

while True:
    user_choice = input("Lights ON or OFF: ")
    if user_choice == 'ON':
        led.on()
        print("Lights ON")
    elif user_choice == 'OFF':
        led.off()
        print("Lights OFF")
    elif user_choice == 'BLINK':
        for _ in range(1, 11):
            led.on()
            sleep(0.2)
            led.off()
            sleep(0.2)
    else:
        print("Unrecognized input...")