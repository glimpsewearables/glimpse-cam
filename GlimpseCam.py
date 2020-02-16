#!/usr/bin/env python

import time, datetime, os, glob, socket, signal
import RPi.GPIO as GPIO
import subprocess as sub
import sys
import logging

BUZZER_PIN = 5
BUZZER_HIGH = 12

def signal_handler(sig, frame):
    logger.info("stopped by keyboard interrupt.")
    logger.info("graceful exit.")
    GPIO.cleanup()
    sys.exit(0)


# TODO: refactor all of this into a setup method called by main
# TODO: watch the GPIO interrupt here, callback should be "main loop"
try: 
    signal.signal(signal.SIGINT, signal_handler)

    # Sets up log
    logFormat='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s'
    logging.basicConfig(
            filename="glimpseLog.log",
            level=logging.DEBUG,
            format=logFormat
    )

    logger = logging.getLogger()

    # Add --console-log argument to add console logging
    if len(sys.argv) > 1 and sys.argv[1] == '--console-log':
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(logging.Formatter(logFormat))
        logger.addHandler(stdout_handler)

    # Global vars
    buttonPressed = False
    prevButtonPress = False
    backlogUploadTime = time.time()

    try:
        # Start pikrellcam and directory watcher
        # Scripts started in .bashrc
        sub.check_call('/home/pi/pikrellcam/pikrellcam &', shell=True)
        time.sleep(8)
        logger.info("pikrellcam start success.")
    except sub.CalledProcessError:
        logger.error("pikrellcam start failed.")

    logger.info("setup success.")
except:
    logger.error("setup failed.")
    print(sys.exc_info()[0])
    raise

#BOOT TEST GOES HERE

#print ("running camera test")
#sub.call('echo "still" > /home/p7/pikrellcam/www/FIFO',shell=True)
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

def buzzMotor(interval = 0.75):
	GPIO.output(BUZZER_PIN, GPIO.HIGH)
	time.sleep(interval)
	GPIO.output(BUZZER_PIN, GPIO.LOW)
	time.sleep(interval)
	GPIO.output(BUZZER_PIN, GPIO.HIGH)
	time.sleep(interval)
	GPIO.output(BUZZER_PIN, GPIO.LOW)


def buzzMotor2():    
        buzzMotor(0.25)
        time.sleep(0.2)
        buzzMotor(0.25)
        time.sleep(0.2)
        buzzMotor(0.25)


def restartCamera():
    try: 
        sub.check_call('/home/pi/pikrellcam/pikrellcam &', shell=True)
        logger.info("restart pikrellcam success.")
        # TODO: remove this sleep
        time.sleep(1)
    except sub.CalledProcessError:
        logger.error("restart pikrellcam failed.")


def checkCamera():
        try:
            # check all processes
            # TODO: remove PIPE
            ps = sub.Popen(('ps','-A'), stdout=sub.PIPE)
            try:
                    output = sub.check_output(('grep','pikrellcam'),stdin=ps.stdout)
                    # TODO: what does this do?
                    ps.wait()
            except sub.CalledProcessError:
                    logger.error("pikrellcam is no longer running")
                    restartCamera()
        except OSError, ValueError:
            logger.error("failed to open process list.");

	
# After booting, motor buzzes twice
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(5, GPIO.OUT)

buzzMotor2()

def record10(): 
    try:
        sub.check_call('echo "record on 10 10" > /home/pi/pikrellcam/www/FIFO', shell=True)
        logger.info("pikrellcam record success.")
	time.sleep(15)
    except sub.CalledProcessError:
        logger.error("pikrellcam record failure.")

def buttonPressResponse():
    try:
        buzzMotor(1.0)
        logger.info("buzz motor success.")
    except:
        logger.info("buzz motor failure.")

# TODO: the "Main loop" code should be called by a signal listening
# for the button press (GPIO.interrupt)
# TODO: remove all shell=True for security and stability
# Main loop
while True:
        # True if the button has been pressed
	buttonPressed = not GPIO.input(12)
	checkCamera()
        # TODO: this condition is supposed to ensures a
        # button press will not interrupt a button press that has
        # happened, although the thread sleeps so it can never reach
        # this state. Preserving for sanity... for now.
	if (buttonPressed and not prevButtonPress):
            logger.info("button pressed, starting record.")
            buttonPressResponse()
            record10()
        elif (buttonPressed):
            logger.info("button pressed during record.")
	time.sleep(0.01)
	prevButtonPress = buttonPressed
