import subprocess
import time
import os


#subprocess.Popen(['/home/pi/picam/picam'], shell=True)
#time.sleep(5)
def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

touch("/home/pi/picam/hooks/start_record")

#touch.touch("~/picam/hooks/start_record")
time.sleep(3)
touch("/home/pi/picam/hooks/stop_record")
