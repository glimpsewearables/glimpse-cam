#!/usr/bin/env python

# Test (in order) Buzzer, button, microphone, then camera
# Run buzzer to beep repeatedly
# Stop with button-press
# Sleep for two seconds
# Have buzzer vibrate with frequency proportional to loudness
# Button press to continue
# Standard camera tests. Button push -> photo, double tap -> video
# end of test script

import time, datetime, os, glob, socket
import RPi.GPIO as GPIO
import subprocess as sub
from logger import log

GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(5, GPIO.OUT)

def buzzTimesInterval( amount, interval ):
    for i in range(amount):
        GPIO.output(5, GPIO.HIGH)
        time.sleep(interval)
        GPIO.output(5, GPIO.LOW)
        time.sleep(interval)

# Run buzzer until button is pressed and released
#currentState = GPIO.input(12)
while GPIO.input() : #currentState or GPIO.input(12) == 0:
    buzzTimesInterval(1, 0.2)
#    currentState = GPIO.input(12)

time.sleep(2)

# Vibrate buzzer proportional to volume until button press
volume = 0
while GPIO.input() :
        buzzTimesInterval(1, 1/(float(volume)))
        #update volume

# internet test
# camera test
# video test
