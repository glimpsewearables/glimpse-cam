#!/usr/bin/env python

import tinys3, socket, os, time, subprocess, json, requests, datetime
from getLines import retKey
from logger import log
from inotify_simple import INotify, flags

# Sets up log
logger = log("errorLog", False).getLogger()

# Getting Access/Secret Keys
l = retKey()
access = l[0]
secret = l[1]

# API endpoint to send data
API_ENDPOINT = "http://52.88.225.198:8000/api/media/"

# Starts aws s3 conncetion
conn = tinys3.Connection(access, secret, tls=True, default_bucket='users-raw-content')

# Set-up for watching directories
watchman = INotify()

# Mask for events that occur in the directories
mask = flags.CLOSE_WRITE

# Function to upload file
def upload(path, filename):
	data = {}
	data["ranking"] = 1
	data["event_id"] = 1
	data["user_id"] = socket.gethostname()[4:]
	data["raw_or_edited"] = "raw"
	data["device_id"] = socket.gethostname()[4:]
	data["downloaded"] = 0
	data["link"] = "https://s3-us-west-2.amazonaws.com/users-raw-content/" + filename + "/"
	data["created_at"] = str(datetime.datetime.fromtimestamp(os.path.getmtime(path+filename)).isoformat("T"))
	data["updated_at"] = str(datetime.datetime.fromtimestamp(os.path.getmtime(path+filename)).isoformat("T"))
	data["media_type"] = "video"
	json_data = json.dumps(data)

	with open(path+filename, 'rb') as f:
		conn.upload(filename, f)
		print(filename + " successfully uploaded!")
		logger.info(filename + " uploaded successfully.")

	requests.post(url=API_ENDPOINT,data=json_data)
	logger.info("metadata for " + filename + " uploaded successfully.")

path = '/home/pi/pikrellcam/media/videos/'
wd = watchman.add_watch(path, mask)

while True:
	# Writes video name to file for uploading
	for event in  watchman.read(timeout=10):
		filetype = event[3][-4:]
		if filetype == '.mp4':
			with open('/home/pi/FilesToUpload.txt','a') as backlog:
				backlog.write(event[3]+'\n')
	# Gets every file needed to be upload
	with open('/home/pi/FilesToUpload.txt','r') as fin:
		data = fin.read().splitlines(True)
	# Uploads in the presence of wifi. Uploads in chronological order and removes it from the upload file if successful
	if not subprocess.check_output(['hostname','-I']).isspace() and data:
		upload(path,data[0].rstrip())
		with open('/home/pi/FilesToUpload.txt','w') as fout:
			fout.writelines(data[1:])
