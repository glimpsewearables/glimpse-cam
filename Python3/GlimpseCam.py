#!/usr/bin/env python

import time, datetime, os, socket
import RPi.GPIO as GPIO
import subprocess as sub
from logger import log

# Constants
BUZZER_PIN = 5
BUZZER_HIGH = 12


# Sets up log
logger = log("errorLog", False).getLogger()
logger.info("Device started.")

# Initialize variables
currentState = False
prevState = False
filename = ""
backlogUploadTime = time.time()

# Start pikrellcam and directory watcher
# Scripts started in .bashrc
sub.call('/home/pi/pikrellcam/pikrellcam &', shell=True)
logger.info("Camera initialized.")
time.sleep(8)

#BOOT TEST GOES HERE

#print ("running camera test")
#sub.call('echo "still" > /home/pi/pikrellcam/www/FIFO',shell=True)
#time.sleep(1)
#filename = rF.rename('/home/pi/pikrellcam/www/media/stills', 0)
#time.sleep(30)
#filepath = 's3://pi-1/' + socket.gethostname() + '/images/' + filename
#try:
#	sub.check_output(['aws', 's3', 'ls', filepath], shell=True)
#except:
#	print 'image file was not uploaded correctly'
	#INSERT HAPTIC FEEDBACK HERE

#IF IT REACHES HERE IT PASSED CAMERA
#print ("running video test")
#sub.call('echo "record on 5 5" > /home/pi/pikrellcam/www/FIFO',shell=True)
#time.sleep(10)
#filename = rF.rename('/home/pi/pikrellcam/www/media/videos', 0)
#time.sleep(60)
#filepath = 's3://pi-1/' + socket.gethostname() + '/videos/' + filename
#try:
#	sub.check_output(['aws', 's3', 'ls', filepath], shell=True)
#except:
#	print 'video file was not uploaded correctly'
	#INSERT HAPTIC FEEDBACK HERE

#BACK TO RUNNING

# After booting, motor buzzes twice
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_HIGH, GPIO.IN, pull_up_down=GPIO.PUD_UP) #setup button
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# vibrate motor
buzzMotor(0.5)

# Main loop
while True:
	currentState = not GPIO.input(12)
	if (currentState and not prevState):
		logger.info("Button pressed once.")
		time.sleep(0.01)
		sub.call('echo "record on 10 10" > /home/pi/pikrellcam/www/FIFO', shell=True) #call camera
		logger.info("Video taken.")
		buzzMotor(0.25)
		time.sleep(10)
	time.sleep(0.01)
	prevState = currentState

# interval parameter determines to buzz interval, default is 0.25
def buzzMotor(self, interval = 0.25):
	self.GPIO.output(BUZZER_PIN, self.GPIO.HIGH)
	time.sleep(interval)
	self.GPIO.output(BUZZER_PIN, self.GPIO.LOW)
	time.sleep(interval)
	self.GPIO.output(BUZZER_PIN, self.GPIO.HIGH)
	time.sleep(interval)
	self.GPIO.output(BUZZER_PIN, self.GPIO.LOW)