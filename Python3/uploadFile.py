#!/usr/bin/env python

import tinys3, socket, pyinotify, os, time, threading, subprocess
import imageEnhance as iE
from getLines import retKey
from logger import log

# Sets up log
logger = log("errorLog", False).getLogger()

# Getting Access/Secret Keys
l = retKey()
access = l[0]
secret = l[1]

# Numbering for images/videos
with open("./glimpse-cam/numFile.txt") as numFile:
	int_list = [int(i) for i in numFile.readline().split()]

# Starts aws s3 conncetion
conn = tinys3.Connection(access, secret, tls=True, default_bucket='pi-5')

# Set-up for watching directories
watchman = pyinotify.WatchManager()

# Mask for events that occur in the directories
mask = pyinotify.IN_MOVED_TO | pyinotify.IN_CREATE

# Exception for if there is no Wifi
class NoWiFiException(Exception):
	pass

# Main class that processes files and uploads them
class EventHandler(pyinotify.ProcessEvent):
	# Uploads a file that is moved into one of the directories after renaming/processing
	def process_IN_MOVED_TO(self, event):
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
					conn.upload(socket.gethostname() + '/' + ('images' if (type == '.jpg') else 'videos') + '/' + filename, f)
					print 'success'
					logger.info(filename + " uploaded successfully.")
				except:
					with open('/home/pi/newFiles.txt','a') as file:
						file.write(event.pathname+'\n')
					print 'failure'
					logger.warning(filename + " failed to upload.")
		threading.Thread(target=__upload, args=[]).start()

	# When a file is created in one of the directories, rename/process the file
	def process_IN_CREATE(self, event):
		type = event.pathname[-4:]
		path = os.path.dirname(event.pathname)
		if type == '.jpg':
			time.sleep(1)
			iE.simpleImageEnhance(event.pathname, event.pathname)
			filename = os.path.basename(event.pathname)
			time.sleep(1)
			os.rename(event.pathname, path + '/%05d' % int_list[0] + filename)
			int_list[0] -= 1
		elif type == '.mp4':
			#print 'video was created: ', event.pathname
			time.sleep(10)
			filename = os.path.basename(event.pathname)
			time.sleep(1)
			os.rename(event.pathname, path + '/%05d' % int_list[1] + filename)
			int_list[1] -= 1
		time.sleep(0.01)
		# Update file numbering
		with open('./glimpse-cam/numFile.txt','w') as numFile:
			numFile.write(str(int_list[0]) + ' ' + str(int_list[1]))

handler = EventHandler()
notifier = pyinotify.Notifier(watchman, handler)
wdd = watchman.add_watch('pikrellcam/media/videos', mask, rec=True)
wss = watchman.add_watch('pikrellcam/media/stills', mask, rec=True)

notifier.loop()