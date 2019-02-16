#!/usr/bin/env python

import tinys3, socket, os, time, subprocess, json, requests, datetime, glob
from getLines import retKey
from logger import log

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

def getEventId():
	now = datetime.datetime.now().time()
	today = datetime.date.today()
	event_id = 1
	if today == "2019-02-07":
		event_id = 5
	elif today == "2019-02-09":
		event_id = 6
	elif today == "2019-02-16":
		event_id = 7
	elif today == "2019-02-17":
		event_id = 8
	elif today == "2019-02-23":
		event_id = 9
	elif today == "2019-02-29":
		event_id = 10
	elif today == "2019-03-07":
		event_id = 11
	elif today == "2019-03-08":
		event_id = 12
	elif today == "2019-03-22":
		event_id = 13
	elif today == "2019-03-23":
		event_id = 14
	elif today == "2019-03-29":
		event_id = 15
	elif today == "2019-04-05":
		event_id = 16
	elif today == "2019-04-06":
		event_id = 17
	elif today == "2019-04-13":
		event_id = 18
	elif today == "2019-04-25":
		event_id = 19
	elif today == "2019-04-27":
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
		# Tries to upload video
		with open(path+filename, 'rb') as f:
			conn.upload(filename, f)
			print(filename + " successfully uploaded!")
			logger.info(filename + " uploaded successfully.")

		# Tries to update API
		try:
			requests.post(url=API_ENDPOINT,data=json_data)
			logger.info("metadata for " + filename + " uploaded successfully.")
		except:
			logger.info("metadata for " + filename + " failed to upload.")

	# Logs upload failure
	except requests.ConnectionError:
		print(filename + " failed to upload.")
		logger.info(filename + " failed to upload.")
		raise ValueError("Upload failed.")

path = '/home/pi/pikrellcam/media/videos/'
list = sorted(glob.glob(path + '*.mp4'),key=os.path.getmtime)
dest = '/home/pi/Videos/'

while True:
	# Uploads in the presence of wifi. Uploads in chronological order and removes it from the upload folder if successful
	if not subprocess.check_output(['hostname','-I']).isspace():
		# Uploads if there are videos left. Checks for new videos after uploading current list.
		if list:
			item = list[0]
			video = os.path.basename(item)
			# Tries uploading video. Moves video and removes it from the list if successful. Otherwise, it stays in the list
			try:
				upload(path, video)
				os.rename(item, dest + video)
				list = list[1:]
			except:
				pass
		else:
			list = sorted(glob.glob(path + '*.mp4'),key=os.path.getmtime)
		time.sleep(2)
