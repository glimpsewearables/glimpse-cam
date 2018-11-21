#!/usr/bin/env python

import time, datetime, os, glob, socket
import RPi.GPIO as GPIO
import subprocess as sub
from logger import log

# Sets up log
jack = log("errorLog", False).getlogger()
jack.info("Device started.")

# Initialize variables
currentState = False
prevState = False
picture = True
filename = ""
backlogUploadTime = time.time()

# Start pikrellcam and directory watcher
sub.call('python /home/pi/glimpse-cam/uploadFile.py &',shell=True)
sub.call('/home/pi/pikrellcam/pikrellcam &',shell=True)
time.sleep(3)

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
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(5, GPIO.OUT)
GPIO.output(5, GPIO.HIGH)
time.sleep(0.5)
GPIO.output(5, GPIO.LOW)
time.sleep(0.5)
GPIO.output(5, GPIO.HIGH)
time.sleep(0.5)
GPIO.output(5, GPIO.LOW)

# Main loop
while True:
	currentState = not GPIO.input(12)
	if (currentState and not prevState):
		jack.info("Button pressed once.")
		picture = True
		time.sleep(0.01)
		endtime = time.time() + 1
		while time.time() < endtime:
			prevState = currentState
			currentState = not GPIO.input(12)
			if (currentState and not prevState):
				jack.info("Button pressed twice.")
				picture = False
				time.sleep(0.01)
				break
			prevState = currentState
			time.sleep(0.01)
		if picture:
			sub.call('echo "still" > /home/pi/pikrellcam/www/FIFO', shell=True)
			jack.info("Image taken.")
			GPIO.output(5, GPIO.HIGH)
			time.sleep(0.5)
			GPIO.output(5, GPIO.LOW)
			time.sleep(1)
		else:
			sub.call('echo "record on 5 5" > /home/pi/pikrellcam/www/FIFO', shell=True)
			jack.info("Video taken.")
			GPIO.output(5, GPIO.HIGH)
			time.sleep(0.25)
			GPIO.output(5, GPIO.LOW)
			time.sleep(0.25)
			GPIO.output(5, GPIO.HIGH)
			time.sleep(0.25)
			GPIO.output(5, GPIO.LOW)
			time.sleep(5)
	# Uploads backlog every 10 minutes
	if time.time() >= backlogUploadTime + 600:
		jack.info("Attempting to upload backlog.")
		backlogUploadTime = time.time()
		print 'Uploading backlog'
		sub.call('python ./glimpse-cam/uploadBacklog.py &', shell=True)
	time.sleep(0.01)
	prevState = currentState
