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
CAMERA = None
SHUTDOWN = False

def signal_handler(sig, frame):
    SHUTDOWN = True # DO NOT REMOVE
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

def restartCamera():
    try: 
        if CAMERA:
            CAMERA.kill()
            CAMERA = sub.Popen(['/home/pi/pikrellcam/pikrellcam'])
            LOGGER.info("restart pikrellcam success.")
        else:
            LOGGER.error("pikrellcam restart called with no camera started.")
    except OSError, ValueError:
        raise RuntimeError("restart pikrellcam failed.")


# Raises RuntimeError
def checkCamera():
    try:
        CAMERA.poll()
        if CAMERA.returncode: 
            LOGGER.error("pikrellcam is no longer running.")
            try:
                restartCamera()
            except RuntimeError as e:
                LOGGER.error(str(e))
    except Exception as e:
        LOGGER.error(str(e))
        raise RuntimeError("failed to open process list.");

def startCamera():
    try:
        CAMERA = sub.Popen(['/home/pi/pikrellcam/pikrellcam'])
        LOGGER.info("pikrellcam start success.")
    except OSError, ValueError:
        LOGGER.error("pikrellcam start failed.")

# TODO: the "Main loop" code should be called by a signal listening
# for the button press (GPIO.interrupt)
# Main loop
# TODO; add in more specific exception handling so that only expected exceptions are handled,
# we don't want to mask exceptions that we don't expect. Check out uploadFile.py for better
# exception handling and logging patterns by always making calling function deal with exception.

def triggerRecord():
    try:
        LOGGER.info("button pressed, starting record.")
        buttonPressResponse()
        record10()
        LOGGER.info("record finished.")
    except RuntimeError as e:
        LOGGER.error(str(e))

def setupCallbacks():
    try:
        RECORD_BUTTON.when_pressed = triggerRecord
        LOGGER.info("setup callbacks success.")
    except Exception as e:
        LOGGER.error(str(e))
        raise RuntimeError("setup callbacks failure.")

def runCamera():
    while not SHUTDOWN:
        # just keep the camera running for now 
        # and let the callbacks handle the rest
        try:
            checkCamera()
        except RuntimeError as e:
            LOGGER.error(str(e))

if __name__=="__main__":
    # setup
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
        #GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(BUZZER_PIN, GPIO.OUT)

        # recognize Glimpse Cam Hardware
        RECORD_BUTTON = Button(BUTTON_PIN)

        startCamera()
        setupCallbacks()

        # buzz motor for success
        buzzMotor2()

        LOGGER.info("setup success.")
    except Exception as e:
        LOGGER.error("setup failed.")
        LOGGER.error(str(e))
        print(sys.exc_info()[0])
        raise

    # run the camera
    runCamera()
