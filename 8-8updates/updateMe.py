from subprocess import call
print "updating.."
call.(["cp", "rc.local", "/etc/rc.local"])
call.(["cp", "blink.service", "/lib/systemd/system/blink.service"])
call.{["systemctl", "daemon-reload"]}
time.sleep(3)
call.(["systemctl", "enable blink.service"])
print "rebooting.."
time.sleep(3)
call.{["reboot"]}
