#!/bin/bash
echo "******************************"
echo "* GlimpseCam Setup Script    *"
echo "******************************"
echo ""

# Update to Latest Version Raspbian
echo ""
echo "-----------------------------"
echo "UPDATE TO LATEST RASPBIAN"
echo "-----------------------------"
echo ""
cd /home/pi
sudo apt-get install
sudo apt-get update

# Install Pikrellcam library
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

# Personalization
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

# Install file upload dependencies
cd /home/pi
pip install tinys3 
echo 'sleep 10' >> .bashrc
echo 'echo $(hostname -I)' >> .bashrc
echo './glimpse-cam/git-update.sh'
echo '#./glimpse-cam/GlimpseCam.py & ./glimpse-cam/uploadFile.py &' >> .bashrc


echo "Congradulations! The Setup is now complete!"
