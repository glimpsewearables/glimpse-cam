import subprocess
host = subprocess.check_output(["hostname", "-I"])
host = host.replace('\n', '')
host = host.replace (' ', '')
if host != "192.168.50.5":
	print "upload enabled"
	call(["python", "uploadFile.py", "--console-log"])
else:
	print "upload disabled"
