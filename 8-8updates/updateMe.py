from subprocess import call
from shutil import copyfile
import time
#copyfile(src, dst)
#call(['npx', 'pinsfw.d', '--sp', '3030'])
print "updating.."
copyfile("/home/pi/glimpse-cam/8-8updates/rc.local","/etc/rc.local")
copyfile("/home/pi/glimpse-cam/8-8updates/blink.service","/lib/systemd/system/blink.service")
#call.(["cp", "rc.local", "/etc/rc.local"])
#call.(["cp", "blink.service", "/lib/systemd/system/blink.service"])
call(["systemctl", "daemon-reload"])
time.sleep(3)
call(["systemctl", "enable", "blink.service"])
print "rebooting.."
time.sleep(3)
call(["reboot"])
