#!/usr/bin/env python

import tinys3, socket, pyinotify, os, time, threading, subprocess, json, requests, datetime
import imageEnhance as iE
from getLines import retKey
from logger import log

# Sets up log
logger = log("errorLog", False).getLogger()

# Getting Access/Secret Keys
l = retKey()
access = l[0]
secret = l[1]

# API endpoint to send data
API_ENDPOINT = "http://52.32.199.147:8000/api/media/"

# Setting up dictionary for json data
data = {}
data["device_id"] = socket.gethostname()[4:]
data["downloaded"] = 0
data["event_id"] = 1
data["ranking"] = 1
data["raw_or_edited"] = "raw"
data["user_id"] = socket.gethostname()[4:]

# Starts aws s3 conncetion
conn = tinys3.Connection(access, secret, tls=True, default_bucket='users-raw-content')

# Set-up for watching directories
watchman = pyinotify.WatchManager()

# Mask for events that occur in the directories
mask = pyinotify.IN_CLOSE_WRITE

# Exception for if there is no Wifi
class NoWiFiException(Exception):
	pass

# Main class that processes files and uploads them
class EventHandler(pyinotify.ProcessEvent):
	# Uploads a file that is moved into one of the directories after renaming/processing
	def process_IN_CLOSE_WRITE(self, event):
		def __upload():
			# Gets file type
            		type = event.pathname[-4:]
			filename = os.path.basename(event.pathname)
			with open(event.pathname, 'rb') as f:
				# Tries uploading. If there is no wifi, backlog the file to upload later
				try:
					if subprocess.check_output(['hostname','-I']).isspace():
						logger.error("No wifi found.")
						raise NoWiFiException()
					conn.upload(filename, f)
					print 'success'
					logger.info(filename + " uploaded successfully.")
					data["link"] = "https://s3-us-west-2.amazonaws.com/users-raw-content/" + filename + "/"
					data["created_at"] = str(datetime.datetime.now().isoformat('T'))
					data["updated_at"] = str(datetime.datetime.now().isoformat('T'))
					data["media_type"] = "image" if (type == '.jpg') else "video"
					json_data = json.dumps(data)
					requests.post(url=API_ENDPOINT,data=json_data)
					logger.info("metadata for " + filename + " uploaded successfully.")
				except:
					with open('/home/pi/FilesToUpload.txt','a') as file:
						file.write(event.pathname+'\n')
					print 'failure'
					logger.warning(filename + " failed to upload.")
		threading.Thread(target=__upload, args=[]).start()

handler = EventHandler()
notifier = pyinotify.Notifier(watchman, handler)
wdd = watchman.add_watch('pikrellcam/media/videos', mask, rec=True)
wss = watchman.add_watch('pikrellcam/media/stills', mask, rec=True)

notifier.loop()
