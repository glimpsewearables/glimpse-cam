import subprocess
import time

def getAddr():	
	hostname = subprocess.check_output(['hostname', '-I'])
	hostname = hostname.replace('\n', '')
	hostname = hostname.split(' ')
	addr = hostname[0] 
	return addr 

def sendMail():
	subprocess.call(['python', '/home/pi/glimpse-cam/mail.py'])

spotAddr = '192.168.50.5'
bootAddr = getAddr() 
i = True

def bootUp():
	bootAddr = getAddr()
	print (getAddr())
	if getAddr() != spotAddr and getAddr() != '':
		sendMail()

def changed():
	print (bootAddr)
	print (getAddr())	
	if bootAddr != getAddr():	
		print ("I changed")
		cleanUp()
	time.sleep(6)
	

def cleanUp():
	print ("A Change is coming")
	if getAddr() == '':
		subprocess.call(['sudo', '/home/pi/Autohotspot/force.sh'])
		print ("Attempting to enter hotspot")
		time.sleep(20)
	if getAddr() != spotAddr: 
		print (getAddr())
		sendMail()
	subprocess.call(['sudo','killall', 'node'])
	subprocess.call(['sudo', 'systemctl',  'restart', 'nextGW.service'])
	#subprocess.call(['sudo','python','/home/pi/glimpse-cam/startServer.py'])
	bootAddr = getAddr()
	print (bootAddr)
	print ("servers restarted")
	
def main():
	bootUp()
	while i:
		print ("got here")
		changed()

main()
