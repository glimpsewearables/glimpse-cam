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
API_ENDPOINT = "https://api.glimpsewearables.com/api/media/"

# Starts aws s3 conncetion
conn = tinys3.Connection(access, secret, tls=True, default_bucket='users-raw-content', endpoint="s3-us-west-2.amazonaws.com")

# Set-up for watching directories
watchman = INotify()

# Mask for events that occur in the directories
mask = flags.CLOSE_WRITE

# Function to upload file
def upload(path, filename):
	now = datetime.datetime.now().time()
    today = datetime.date.today()
	data = {}
	data["ranking"] = 1
	data["event_id"] = 4
	data["user_id"] = socket.gethostname()[4:]
	data["raw_or_edited"] = "raw"
	data["device_id"] = socket.gethostname()[4:]
	data["downloaded"] = 0
	data["link"] = "https://s3-us-west-2.amazonaws.com/users-raw-content/" + filename
	data["created_at"] = str(datetime.datetime.fromtimestamp(os.path.getmtime(path+filename)).isoformat("T"))
	data["updated_at"] = str(datetime.datetime.fromtimestamp(os.path.getmtime(path+filename)).isoformat("T"))
	data["media_type"] = "video"
	data["downloaded"] = 0
	data["date"] = str(today)
	data["date_time"] = str(now)
	data["gif_link"] = ""
	# data["media_length"] = 0.0
	# data["media_size"] = 0.0
	# data["user_rating"] = 0
	# data["curator_rating"] = 0
	# data["bitrate"] = 0
	# data["total_bitrate"] = 0
	json_data = json.dumps(data)

	try:
		with open(path+filename, 'rb') as f:
			conn.upload(filename, f)
			print(filename + " successfully uploaded!")
			logger.info(filename + " uploaded successfully.")
			
		try:
			requests.post(url=API_ENDPOINT,data=json_data)
			logger.info("metadata for " + filename + " uploaded successfully.")
		except:
			logger.info("metadata for " + filename + " failed to upload.")
	except requests.ConnectionError:
		print(filename + " failed to upload.")
		logger.info(filename + " failed to upload.")
		raise ValueError("Upload failed.")

path = '/home/pi/pikrellcam/media/videos/'
wd = watchman.add_watch(path, mask)

while True:
	# Writes video name to file for uploading
	for event in  watchman.read(timeout=10):
		filetype = event[3][-4:]
		if filetype == '.mp4':
			with open('/home/pi/FilesToUpload.txt','a') as backlog:
				backlog.write(event[3]+'\n')
	# Uploads in the presence of wifi. Uploads in chronological order and removes it from the upload file if successful
	if not subprocess.check_output(['hostname','-I']).isspace():
		# Gets every file needed to be upload
		with open('/home/pi/FilesToUpload.txt','r') as fin:
			data = fin.read().splitlines(True)
		if data:
			try:
				upload(path,data[0].rstrip())
				with open('/home/pi/FilesToUpload.txt','w') as fout:
					fout.writelines(data[1:])
			except:
				pass
