#!/usr/bin/env python

import tinys3, socket, os, time, subprocess, json, requests, datetime, glob, httplib, traceback
from getLines import retKey
from logger import log

# Sets up log
logger = log("errorLog", False).getLogger()

# Getting Access/Secret Keys
l = retKey()
access = l[0]
secret = l[1]

# API endpoint to send data
API_ENDPOINT = "http://api.glimpsewearables.com/api/media/"

# Cloudinary URL 
CLOUDINARY_URL = "www.res.cloudinary.com"

# Cloudinary prefix
CLOUDINARY_METHOD = "/glimpse-wearables/video/upload"

# Create global HTTP connection since these are expensive 
# TODO: maybe clean this up in a later iteration 
httpConn = httplib.HTTPConnection(CLOUDINARY_URL)

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

# Hits cloudinary url to trigger file upload from AWS
# Returns True if trigger succeeds, False if failed.
def upload_cloudinary(user_id, filename):

	if not user_id:
		logger.error("Cloudinary upload called with no user_id.")
		return False
	if not filename:
		logger.error("Cloudinary upload called with no filename.")
		return False
	
	req_url = "{}/{}/{}".format(CLOUDINARY_METHOD, user_id, filename)

        try:
            # Use HEAD since no data is required
            httpConn.request("HEAD", req_url)
        except Exception as e:
                traceback.print_exc()
                logger.error("Cloudinary request failed for {}.".format(req_url))
                return False

        cloudinary_return = False
        cloudinary_attempts = 0

        # Retry Cloudinary trigger until success or at most 3 times
        while not cloudinary_return and cloudinary_attempts < 3:
            try:
                resp = httpConn.getresponse()
                cloudinary_attempts += 1
                if resp.status != 200:
                        # Cloudinary failed, return from method
                        logger.error("Cloudinary HTTP HEAD status {} reason {} for {}.".format(resp.status, resp.reason, req_url))
                        return False
                else:
                        # Read the response to enabled next request
                        resp.read()
                        cloudinary_return = True
                        logger.info("Cloudinary upload triggered for {}.".format(req_url))
            except httplip.ResponseNotReady as e:
                logger.info("Cloudinary HTTP response for {} not ready after attempt {}, retrying...".format(req_url, cloudinary_attempts))
        
        # The request never returned
        if not cloudinary_return:
                logger.error("Cloudinary HTTP request for {} never returned.".format(req_url))
                return False

        return True

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

		upload_cloudinary(socket.gethostname()[:4], filename)

		# Tries to update API
		try:
			requests.post(url=API_ENDPOINT,data=json_data)
			logger.info("metadata for " + filename + " uploaded successfully.")
		except:
			logger.error("metadata for " + filename + " failed to upload.")

	# Logs upload failure
	except requests.ConnectionError:
		print(filename + " failed to upload.")
		logger.error(filename + " failed to upload.")
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
			except Exception as e:
                                logger.error("{} upload / move failed.".format(video))
				pass
		else:
			list = sorted(glob.glob(path + '*.mp4'),key=os.path.getmtime)
		time.sleep(2)
