USERNAME = "raspberrypi"
RECORD_TIME = 10

def checkFile():
	path = 'home/pi/pikrellcam/media/videos'
	file = USERNAME + '_video_' + time.strftime('%Y-%m-%d_%H.%M.%S', time.localtime()) + '.mp4'
	time.sleep(RECORD_TIME)
	if (path.exists(path + file)):
		LOGGER.info("File Creation Success")
	else:
		raise RuntimeError("File Creation Error")
