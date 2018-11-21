#!/usr/bin/env python

import time, datetime, os, glob, socket, tinys3, threading, socket
from shutil import copyfile
import subprocess as sub
from getLines import retKey
from logger import log

# Sets up log
jack = log("errorLog", False).getlogger()

# for getting the access and secret
l = retKey()
access = l[0]
secret = l[1]

conn = tinys3.Connection(access, secret, tls=True, default_bucket = 'pi-5')

copyfile('/home/pi/newFiles.txt','/home/pi/FilesToUpload.txt')
with open('/home/pi/FilesToUpload.txt') as f:
	content = [x.strip() for x in f]
	open('/home/pi/newFiles.txt', 'w').close()

class NoWiFiException(Exception):
	pass

def __upload(file):
	type = file[-4:]
	filename = os.path.basename(file)
	with open(file, 'rb') as f:
		try:
			if sub.check_output(['hostname','-I']).isspace():
				jack.error("No wifi found when uploading backlog.")
				raise NoWiFiException()
			conn.upload(socket.gethostname() + '/' + ('images' if (type == '.jpg') else 'videos') + '/' + filename, f)
			print 'successful upload'
			jack.info(filename + " uploaded successfully from backlog.")
		except:
			with open('/home/pi/newFiles.txt','a') as newfile:
				newfile.write(file+'\n')
			print 'wrote '+file+' to newFiles.txt'
			jack.warning(filename + " failed to upload from backlog.")

while content:
	threading.Thread(target=__upload, args=[content.pop(0)]).start()
