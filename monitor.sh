while true
do
	gpio -g read 4 > battery.csv
	uptime -p >> battery.csv
	date >> battery.csv
	hostname -I >> battery.csv
	aws s3 cp "battery.csv" s3://pi-1/$(hostname)/
	sleep 60
done
