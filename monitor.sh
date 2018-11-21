while true
do
	gpio -g read 4 > battery.csv
	uptime -p >> battery.csv
	date >> battery.csv
	hostname -I >> battery.csv
	#python -c "import tinys3, socket, sys; sys.path.insert(0, '/home/pi/glimpse-cam'); import getLines as decode; A=decode.retKey(); conn=tinys3.Connection(A[0],A[1],tls=True,default_bucket='pi-5'); f=open('battery.csv','rb'); conn.upload(socket.gethostname()+'/battery.csv',f);"
	sleep 60
done
