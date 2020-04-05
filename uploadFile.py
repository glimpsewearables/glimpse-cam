#!/usr/bin/env python
import tinys3, socket, os, time, subprocess, requests, glob
import logging
import sys

def retKey():
    lines = []
    with open("/home/pi/glimpse-cam/keys.txt") as f:
        for line in f:
            lines.append(line.strip())
    return lines

try: 
    # Sets up log
    logFormat='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s'
    logging.basicConfig(
            filename="uploadLog.log",
            level=logging.INFO,
            format=logFormat
    )

    logger = logging.getLogger()

    # Add --console-log argument to add console logging
    if len(sys.argv) > 1 and sys.argv[1] == '--console-log':
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(logging.Formatter(logFormat))
        logger.addHandler(stdout_handler)

    # Getting Access/Secret Keys
    l = retKey()
    access = l[0]
    secret = l[1]

    # API endpoint to send data
    API_ENDPOINT = "http://api.glimpsewearables.com/api/media/"
    TO_UPLOAD_PATH = '/home/pi/pikrellcam/media/videos/'
    list = sorted(glob.glob(TO_UPLOAD_PATH + '*.mp4'),key=os.path.getmtime)
    UPLOADED_PATH = '/home/pi/Videos/'
    UPLOAD_COMPLETE_MESSAGE = False

    # Starts aws s3 conncetion
    conn = tinys3.Connection(access, secret, tls=True, default_bucket='users-raw-content', endpoint="s3-us-west-2.amazonaws.com")
    logger.info("setup success.")
except:
    logger.error("setup failed.")
    print(sys.exc_info()[0])
    raise

def aws_upload(path, filename):
        # Tries to upload video
        with open(path+filename, 'rb') as f:
                conn.upload(filename, f)

# TODO: refactor this to be asynchronous signals not a loop always running :(
# TODO: add in better logging where possible and more specific exception handling
# TODO: remove unecessary sleeps when stability is established
# TODO: refactor class constants and parameters
while True:
	# Uploads in the presence of wifi. Uploads in chronological order and removes it from the upload folder if successful
	if not subprocess.check_output(['hostname','-I']).isspace():
		# Uploads if there are videos left. Checks for new videos after uploading current list.
		if list:
			item = list[0]
			video = os.path.basename(item)
			# Tries uploading video. Moves video and removes it from the list if successful. Otherwise, it stays in the list
			try:
                                aws_upload(TO_UPLOAD_PATH, video)
                                # does not move video unless AWS upload is exception free
				os.rename(item, UPLOADED_PATH + video)
				list = list[1:]
                                logger.info("AWS upload for {} success.".format(video))
			except Exception as e:
                                logger.error(str(e))
		else:
			list = sorted(glob.glob(TO_UPLOAD_PATH + '*.mp4'),key=os.path.getmtime)
                        if len(list) == 0: 
                            # wait 5 seconds to check for new videos if none
                            if not UPLOAD_COMPLETE_MESSAGE:
                                logger.info("all video uploads are complete.") 
                                UPLOAD_COMPLETE_MESSAGE = True
		            time.sleep(5)
                        elif len(list) > 0: 
                            UPLOAD_COMPLETE_MESSAGE = False
        else:
            # wait a few seconds to check for WiFi
            time.sleep(10) 
