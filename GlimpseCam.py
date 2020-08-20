#!/usr/bin/env python

import time, datetime, os, glob, socket, signal 
import RPi.GPIO as GPIO 
import subprocess as sub 
import sys 
import logging 
from gpiozero import Button


# Global variables
BUZZER_PIN = 5 
BATTERY_PIN = 4
BUTTON_PIN = 12 
LOGGER = None
RECORD_BUTTON = None
SHUTDOWN = False
CAMERA = None
BATTERY = None
CAMERA_COMMAND = ['/home/pi/pikrellcam/pikrellcam']
CAMERA_PROCESS_NAME = 'pikrellcam'
RECORD_TIME = 10
RECORD_RETRO_COMMAND = 'echo "record on {} {}" > /home/pi/pikrellcam/www/FIFO'.format(RECORD_TIME, RECORD_TIME)
RECORD_REG_COMMAND = 'echo "record on {}" > /home/pi/pikrellcam/www/FIFO'.format(RECORD_TIME, RECORD_TIME)
STILL_COMMAND = 'echo "still" > /home/pi/pikrellcam/www/FIFO'
MODE_MAP = {'RECORD_RETRO': RECORD_RETRO_COMMAND, 'RECORD_REG': RECORD_REG_COMMAND, 'STILL': STILL_COMMAND}
USERNAME = 'raspberrypi'
VIDEO_FILE_PATH = "/home/pi/pikrellcam/media/videos/"

def signal_handler(sig, frame):
    global SHUTDOWN
    SHUTDOWN = True # DO NOT REMOVE
    LOGGER.info("stopped by keyboard interrupt.")
    LOGGER.info("graceful exit.")
    GPIO.cleanup(BUZZER_PIN)

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

def recordModal(mode):
    """
    Sends command given by mode to pikrellcam FIFO.
    Raises RuntimeError if process call fails.
    """
    global MODE_MAP
    try:
        sub.check_call(MODE_MAP[mode], shell=True)
        LOGGER.info("pikrellcam {} start success.".format(mode))
    except sub.CalledProcessError:
        raise RuntimeError("pikrellcam record failure.")

def buttonPressResponse():
    try:
        buzzMotor(1.0)
	LOGGER.info("buzz motor success.")
    except:
        raise RuntimeError("buzz motor failure.")

def checkFileBefore():
	temp = len([name for name in os.listdir(VIDEO_FILE_PATH) if os.path.isfile(os.path.join(VIDEO_FILE_PATH, name))])
	LOGGER.info(temp)
	return temp

def checkFileAfter(file, numBefore):
	LOGGER.info("Checking for:" + file)
	time.sleep(2.0)
	currNum = checkFileBefore()
        listOfFiles = glob.glob(VIDEO_FILE_PATH + "*.mp4")
        mostRecentFile = max(listOfFiles, key=os.path.getctime) 
        if (currNum - numBefore) == 1 and (os.path.isfile(mostRecentFile)):
                LOGGER.info("File Creation Success")
        else:
                raise RuntimeError("File creation failure") 

def checkCamera():
    """ 
    Checks if pikrellcam is running.
    Return True if running in either this or another process.
    Return False if not running.
    Raise RuntimeError if check fails.
    """
    global CAMERA
    try:
        if CAMERA:
            CAMERA.poll()
            if CAMERA.returncode is None: 
                return True
            else:
                killCamera()
            LOGGER.error("pikrellcam was started in this process but is no longer running.")
        elif CAMERA_PROCESS_NAME in sub.check_output(['ps', '-A'], shell=True):
            # LOGGER.info("pikrellcam is running in seperate process.")
            return True
        return False
    except Exception as e:
        LOGGER.error(str(e))
        raise RuntimeError("failed to check camera.");

def startCamera():
    global CAMERA, CAMERA_COMMAND
    try:
        CAMERA = sub.Popen(CAMERA_COMMAND)
        LOGGER.info("pikrellcam start success.")
    except OSError, ValueError:
        raise RuntimeError("pikrellcam start failed.")

def killCamera():
    global CAMERA
    try:
        if CAMERA is not None:
            CAMERA.kill()
    except Exception as e:
        LOGGER.error(str(e))
        LOGGER.error("failed to kill camera.")

def runCamera():
    while not SHUTDOWN:
        # just keep the camera running for now 
        # and let the callbacks handle the rest
	try:
            if not checkCamera():
                startCamera()
        except RuntimeError as e:
            LOGGER.error(str(e))
	time.sleep(.1)
    killCamera()

def triggerDeviceRecord():
    try:
        LOGGER.info("button pressed, starting record.")
        buttonPressResponse()
	file = USERNAME + '_video_' + time.strftime('%Y-%m-%d_%H.%M.%S', time.localtime(time.time() - 10)) + '.mp4'
	numBefore = checkFileBefore()
	recordModal('RECORD_RETRO')
	time.sleep(RECORD_TIME)
	checkFileAfter(file, numBefore)
    except RuntimeError as e:
        LOGGER.error(str(e))

def lowBatteryLog():
    LOGGER.info("low battery.")

def setupCallbacks():
    try:
        RECORD_BUTTON.when_pressed = triggerDeviceRecord
        BATTERY.when_pressed = lowBatteryLog
        LOGGER.info("setup callbacks success.")
    except Exception as e:
        LOGGER.error(str(e))
        raise RuntimeError("setup callbacks failure.")

def setupLogger():
    # Sets up log, if this fails we're screwed.
    global LOGGER
    logFormat='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s'
    logging.basicConfig(
            filename="/home/pi/glimpse-cam/glimpseLog.log",
            level=logging.DEBUG,
            format=logFormat
    )
    LOGGER = logging.getLogger()

    # Add --console-log argument to add console logging
    if '--console-log' in sys.argv:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(logging.Formatter(logFormat))
        LOGGER.addHandler(stdout_handler)

def setupFakeCamera():
    global CAMERA_COMMAND, CAMERA_PROCESS_NAME, MODE_MAP
    # represents a fake pikrellcam that will die every 1 minute
    CAMERA_COMMAND = ['sleep', '1m']
    # configure process to match pikrellcam command
    CAMERA_PROCESS_NAME = 'sleep'
    # set all mode actions to a fake command 
    MODE_MAP = dict.fromkeys(MODE_MAP, 'echo "fake camera mode"')


def setupCamera():
    if '--fake-cam' in sys.argv:
        setupFakeCamera()
    # check if the camera is setup
    if not checkCamera():
        # if not then setup the camera
        startCamera()

def setupDevice():
    global RECORD_BUTTON, BATTERY
    # setup the Buzzer
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUZZER_PIN, GPIO.OUT)

    # recognize Glimpse Cam Hardware
    RECORD_BUTTON = Button(BUTTON_PIN)
    # low battery warning sent when pin 4 pulled low
    # only read button click every 60s
    BATTERY = Button(BATTERY_PIN, pull_up=False, bounce_time=60)
    setupCallbacks()
    # buzz motor for success
    buzzMotor2()

if __name__=="__main__":
    # setup logger always
    try: 
        setupLogger()
        LOGGER.info("setup logger success.")
    except Exception as e:
        print(sys.exc_info()[0])
        raise

    # setup camera always
    try: 
        setupCamera()
        LOGGER.info("setup camera success.")
    except Exception as e:
        LOGGER.error("setup camera failed.")
        LOGGER.error(str(e))
        print(sys.exc_info()[0])
        raise

    # TODO: cleanup this logic to be agnostic of order
    # cosider using a CLI library that handles arg parsing.
    if '--record-reg' in sys.argv:
        recordModal('RECORD_REG')
    elif '--record-retro' in sys.argv:
        recordModal('RECORD_RETRO')
    elif '--still' in sys.argv:
        recordModal('STILL')
    else:
        # setup and run device
        try: 
            signal.signal(signal.SIGINT, signal_handler)
            setupDevice()
            LOGGER.info("setup device success.")
        except Exception as e:
            LOGGER.error("setup device failed.")
            LOGGER.error(str(e))
            print(sys.exc_info()[0])
            raise
        # run the camera
        runCamera()
