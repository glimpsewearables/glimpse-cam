from subprocess import call
print "updating.."
call.(["mv", "rc.local", "/etc/"])
call.(["mv", "blink.service", "/lib/systemd/system/"])
call.{["systemctl", "daemon-reload"]}
time.sleep(3)
call.(["systemctl", "enable blink.service"])
print "rebooting.."
time.sleep(3)
call.()
