#!/usr/bin/env python 
import time, datetime, os, glob, socket, signal 
import RPi.GPIO as GPIO 
import subprocess as sub 
import sys 
import logging 
from gpiozero import Button

# Global variables
BUZZER_PIN = 5 
BUTTON_PIN = 12 
LOGGER = None
RECORD_BUTTON = None

def signal_handler(sig, frame):
    LOGGER.info("stopped by keyboard interrupt.")
    LOGGER.info("graceful exit.")
    GPIO.cleanup()
    sys.exit(0)

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

# Raises RuntimeError if fails to record
def record10(): 
    try:
        sub.check_call('echo "record on 10 10" > /home/pi/pikrellcam/www/FIFO', shell=True)
        LOGGER.info("pikrellcam record success.")
        # sleep only for 10 seconds since this is the time to record
	time.sleep(10)
    except sub.CalledProcessError:
        raise RuntimeError("pikrellcam record failure.")

def buttonPressResponse():
    try:
        buzzMotor(1.0)
        LOGGER.info("buzz motor success.")
    except:
        raise RuntimeError("buzz motor failure.")

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

def restartCamera():
    try: 
        sub.check_call('/home/pi/pikrellcam/pikrellcam &', shell=True)
        LOGGER.info("restart pikrellcam success.")
        # TODO: remove this sleep
        time.sleep(1)
    except sub.CalledProcessError:
        raise RuntimeError("restart pikrellcam failed.")


# Raises RuntimeError
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
                    LOGGER.error("pikrellcam is no longer running.")
                    try:
                        restartCamera()
                    except RuntimeError:
                        LOGGER.error(str(e))
        except OSError, ValueError:
            raise RuntimeError("failed to open process list.");

def startCamera():
        try:
            # Start pikrellcam and directory watcher
            # Scripts started in .bashrc
            sub.check_call('/home/pi/pikrellcam/pikrellcam &', shell=True)
            time.sleep(8)
            LOGGER.info("pikrellcam start success.")
        except sub.CalledProcessError:
            LOGGER.error("pikrellcam start failed.")

# TODO: the "Main loop" code should be called by a signal listening
# for the button press (GPIO.interrupt)
# TODO: remove all shell=True for security and stability
# Main loop
# TODO; add in more specific exception handling so that only expected exceptions are handled,
# we don't want to mask exceptions that we don't expect. Check out uploadFile.py for better
# exception handling and logging patterns by always making calling function deal with exception.

if __name__=="__main__":
    try: 
        # Sets up log, if this fails we're screwed.
        logFormat='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s'
        logging.basicConfig(
                filename="glimpseLog.log",
                level=logging.DEBUG,
                format=logFormat
        )

        LOGGER = logging.getLogger()

        # Add --console-log argument to add console logging
        if len(sys.argv) > 1 and sys.argv[1] == '--console-log':
            stdout_handler = logging.StreamHandler(sys.stdout)
            stdout_handler.setLevel(logging.DEBUG)
            stdout_handler.setFormatter(logging.Formatter(logFormat))
            LOGGER.addHandler(stdout_handler)
        # setup signal handler for kill signal
        signal.signal(signal.SIGINT, signal_handler)

        # setup the Buzzer
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(BUZZER_PIN, GPIO.OUT)

        # recognize Glimpse Cam Hardware
        #RECORD_BUTTON = Button(BUTTON_PIN)

        startCamera()
        
        # buzz motor for success
        buzzMotor2()

        LOGGER.info("setup success.")
    except:
        LOGGER.error("setup failed.")
        print(sys.exc_info()[0])
        raise
    # camera handles all exceptions once running
    while True:
            buttonPressed = not GPIO.input(12)
            # Always check the camera is running
            try:
                checkCamera()
            except RuntimeError:
                LOGGER.error(str(e))
            # TODO: this condition is supposed to ensures a
            # button press will not interrupt a button press that has
            # happened, although the thread sleeps so it can never reach
            # this state. Preserving for sanity... for now.
            # if button pressed and not prevButtonPressed
            if buttonPressed: 
                LOGGER.info("button pressed, starting record.")
                try:
                    buttonPressResponse()
                    record10()
                except RuntimeError:
                    LOGGER.error(str(e))

