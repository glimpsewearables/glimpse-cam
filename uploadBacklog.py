#!/usr/bin/env python

import time, datetime, os, glob, socket, tinys3, threading, socket, json, requests
from shutil import copyfile
import subprocess as sub
from getLines import retKey
from logger import log

# Sets up log
logger = log("errorLog", False).getLogger()

# for getting the access and secret
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

with open('/home/pi/FilesToUpload.txt', 'r') as fin:
    data = fin.read().splitlines(True)
with open('/home/pi/FilesToUpload.txt', 'w') as fout:
    fout.writelines(data[1:])

class NoWiFiException(Exception):
	pass

def __upload(file):
	type = file[-4:]
	filename = os.path.basename(file)
	with open(file, 'rb') as f:
		try:
			if sub.check_output(['hostname','-I']).isspace():
				logger.error("No wifi found when uploading backlog.")
				raise NoWiFiException()
			conn.upload(filename, f)
			print 'successful upload'
			logger.info(filename + " uploaded successfully from backlog.")
			data["link"] = "https://s3-us-west-2.amazonaws.com/users-raw-content/" + filename + "/"
			data["created_at"] = str(datetime.datetime.fromtimestamp(os.path.getmtime(file)).isoformat('T'))
			data["updated_at"] = str(datetime.datetime.fromtimestamp(os.path.getmtime(file)).isoformat('T'))
			data["media_type"] = "image" if (type == '.jpg') else "video"
			json_data = json.dumps(data)
			requests.post(url=API_ENDPOINT,data=json_data)
			logger.info("metadata for " + filename + " uploaded successfully form backlog.")
		except:
			with open('/home/pi/FilesToUpload.txt','a') as newfile:
				newfile.write(file+'\n')
			print 'wrote '+file+' to newFiles.txt'
			logger.warning(filename + " failed to upload from backlog.")

try:
	threading.Thread(target=__upload, args=[data[0]]).start()
except:
	pass
