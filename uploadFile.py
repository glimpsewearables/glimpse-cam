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

def getEventId():
	now = datetime.datetime.now().time()
	today = datetime.date.today()
	event_id = 1
	if today == "2019-02-07":
		event_id = 5
	elif today == "2019-02-09"
		event_id = 6
	elif today == "2019-02-16"
		event_id = 7
	elif today == "2019-02-17"
		event_id = 8
	elif today == "2019-02-23"
		event_id = 9
	elif today == "2019-02-29"
		event_id = 10
	elif today == "2019-03-07"
		event_id = 11
	elif today == "2019-03-08"
		event_id = 12
	elif today == "2019-03-22"
		event_id = 13
	elif today == "2019-03-23"
		event_id = 14
	elif today == "2019-03-29"
		event_id = 15
	elif today == "2019-04-05"
		event_id = 16
	elif today == "2019-04-06"
		event_id = 17
	elif today == "2019-04-13"
		event_id = 18
	elif today == "2019-04-25"
		event_id = 19
	elif today == "2019-04-27"
		event_id = 20
	return event_id

# Function to upload file
def upload(path, filename):
	now = datetime.datetime.now().time()
	today = datetime.date.today()
	data = {}
	data["ranking"] = 1
	data["event_id"] = getEventId()
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
