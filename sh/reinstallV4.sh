#!/bin/bash
echo "******************************"
echo "* GlimpseCam Setup Script    *"
echo "* Developed by Tianhao Zhang *"
echo "* Modified by Justin Ngo     *"
echo "* Copyright (C) 2018         *"
echo "******************************"
echo ""

if [ $# -eq 0 ]; then
	echo "Which Module(s) Would You Like to Install?"
	echo "(1) Update to Latest Raspbian"
	echo "(2) Install Pikrellcam Library"
	echo "(3) Personalization"
	echo "(4) Install ALL"
	read -p "Please Enter Your Selection (1-4): " ANSWER
else
	ANSWER=$1
fi

if [[ $ANSWER != [1-4] ]]; then
	echo "INVALID SELECTION!"
	exit 1
fi

# Update to Latest Version Raspbian
if [ $ANSWER -eq 1 -o $ANSWER -eq 6 -o $ANSWER -eq 7 ]; then
	echo ""
	echo "-----------------------------"
	echo "UPDATE TO LATEST RASPBIAN"
	echo "-----------------------------"
	echo ""
	cd /home/pi
	sudo apt-get install
	sudo apt-get update
fi

# Install Pikrellcam library
if [ $ANSWER -eq 2 -o $ANSWER -eq 6 -o $ANSWER -eq 7 ]; then
	echo ""
	echo "-----------------------------"
	echo "INSTALL PIKRELLCAM LIBRARY"
	echo "-----------------------------"
	echo ""
	cd /home/pi
	git clone https://github.com/billw2/pikrellcam
	cd pikrellcam
	chmod u+rwx install-pikrellcam.sh
	./install-pikrellcam.sh
	sudo mv /home/pi/glimpse-cam/sh/pikrellcam.conf /home/pi/.pikrellcam/pikrellcam.conf
fi

# Personalization
if [ $ANSWER -eq 3 -o $ANSWER -eq 6 -o $ANSWER -eq 7 ]; then
	echo ""
	echo "-----------------------------"
	echo "Please Set Up the TimeZone Information."
	echo "-----------------------------"
	sleep 3
	sudo dpkg-reconfigure tzdata
	echo "-----------------------------"
	echo "Please Change the Default Password and "
	echo "Enable the Camera, SSH, and I2S through Interface Options."
	echo "-----------------------------"
	sleep 3
	sudo raspi-config
	echo ""
fi

# Install file upload dependencies
cd /home/pi
pip install tinys3
sudo apt-get install python-setuptools
sudo easy_install pyinotify
echo '#./glimpse-cam/GlimpseCam.py' >> .bashrc
>newFiles.txt

echo "Congradulations! The Setup is now complete!"
