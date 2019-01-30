#!/usr/bin/env python

import time, datetime, os, glob, socket
import RPi.GPIO as GPIO
import subprocess as sub

BUZZER_PIN = 5
BUZZER_HIGH = 12

# Initialize variables
currentState = False
prevState = False
picture = True
filename = ""
backlogUploadTime = time.time()

response = input("Buzzer Test. Press any key to continue...")
buzzMotor()
response = input("Did buzzer vibrate? If not, buzzer is not attached correctly.")

print("Testing Microphone")
os.system("arecord -l")
response = input("Do you see the microphone? If not, microphone is not connected correctly.")


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
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(5, GPIO.OUT)

buzzMotor(0.5)
# Replaced with buzzMotor function. If it doesnt work, revert back to below code - Stefan
# GPIO.output(5, GPIO.HIGH)
# time.sleep(0.5)
# GPIO.output(5, GPIO.LOW)
# time.sleep(0.5)
# GPIO.output(5, GPIO.HIGH)
# time.sleep(0.5)
# GPIO.output(5, GPIO.LOW)


# Main loop
while True:
	currentState = not GPIO.input(12)
	if (currentState and not prevState):
		logger.info("Button pressed once.")
		time.sleep(0.01)
		sub.call('echo "record on 10 10" > /home/pi/pikrellcam/www/FIFO', shell=True)
		#pikrellcam record on 10 10 > 
		logger.info("Video taken.")
		
		buzzMotor(0.25)
		# Replaced with buzzMotor function. If it doesnt work, revert back to below code - Stefan
		# GPIO.output(5, GPIO.HIGH)
		# time.sleep(0.25)
		# GPIO.output(5, GPIO.LOW)
		# time.sleep(0.25)
		# GPIO.output(5, GPIO.HIGH)
		# time.sleep(0.25)
		# GPIO.output(5, GPIO.LOW)
		time.sleep(10)
	time.sleep(0.01)
	prevState = currentState

def buzzMotor(self, interval = 0.25):
	self.GPIO.output(BUZZER_PIN, self.GPIO.HIGH)
	time.sleep(interval)
	self.GPIO.output(BUZZER_PIN, self.GPIO.LOW)
	time.sleep(interval)
	self.GPIO.output(BUZZER_PIN, self.GPIO.HIGH)
	time.sleep(interval)
	self.GPIO.output(BUZZER_PIN, self.GPIO.LOW)