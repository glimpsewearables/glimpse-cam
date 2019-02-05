#!/usr/bin/env python

import time, datetime, os, glob, socket
import RPi.GPIO as GPIO
import subprocess as sub

def buzzMotor(self, interval = 0.25):
	self.GPIO.output(BUZZER_PIN, self.GPIO.HIGH)
	time.sleep(interval)
	self.GPIO.output(BUZZER_PIN, self.GPIO.LOW)
	time.sleep(interval)
	self.GPIO.output(BUZZER_PIN, self.GPIO.HIGH)
	time.sleep(interval)
	self.GPIO.output(BUZZER_PIN, self.GPIO.LOW)

BUZZER_PIN = 5
BUZZER_HIGH = 12

# Initialize variables
currentState = False
prevState = False
picture = True
filename = ""
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(5, GPIO.OUT)


response = str(input("Buzzer Test. Press any key to continue..."))
buzzMotor()
response = str(input("Did buzzer vibrate? If not, buzzer is not attached correctly."))

print("Testing Microphone")
os.system("arecord -l")
response = str(input("Do you see the microphone? If not, microphone is not connected correctly."))

print("Testing Camera")
sub.call('/home/pi/pikrellcam/pikrellcam &', shell=True)
time.sleep(3)
response = str(input("Any errors thrown? If not, continue"))

#Justin I need you to make sure the below code is still relevant and correct
print ("Running video test")
sub.call('echo "record on 5 5" > /home/pi/pikrellcam/www/FIFO',shell=True)
time.sleep(10)
filename = rF.rename('/home/pi/pikrellcam/www/media/videos', 0)
time.sleep(60)
filepath = 's3://pi-1/' + socket.gethostname() + '/videos/' + filename
try:
	sub.check_output(['aws', 's3', 'ls', filepath], shell=True)
except:
	print ('video file was not uploaded correctly')
#Up to here.

response = str(input("End of Test Script. Press any key to exit"))