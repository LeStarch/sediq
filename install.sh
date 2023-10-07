#!/bin/sh
##
# Settings
##
KODI=~/.kodi/userdata/
HERE=`dirname $0`
HERE=`cd ${HERE}; pwd`
##
# Sediq required packages
##
sudo apt-get install \
  git \
  vim \
  gstreamer1.0-tools \
  gstreamer1.0-plugins-base \
  gstreamer1.0-plugins-good \
  rtl-sdr 
##
# Update submodules
##
OCWD=`pwd`
cd ${HERE}
git submodule update --init --recursive
cd ${OCWD}
##
# Link in the installed library
##
cd ${OCWD}
##
# Aux video files
##
cd ${KODI}
ln -s ${HERE}/camera/playercorefactory.xml
cd ${OCWD}
cd  /lib/systemd/system/
sudo ln -fs ${HERE}/deathclock.service
sudo ln -fs ${HERE}/radio-service/radio-service.service
sudo systemctl enable deathclock
sudo systemctl enable radio-service
cd ${OCWD}
##
# Add in skin, and radio plugins
##
cd ~/.kodi/addons
ln -s ${HERE}/skin.sediqskin
ln -s ${HERE}/plugin.audio.sediq
cd ${OCWD}
##
# Boot options for iqcaudio and boot speed
##
##
# Install the RTL rules and modprobe setup
##
sudo cp rtl-sdr.rules /etc/udev/rules.d/99-rtl-sdr.rules
sudo cp ./blacklist-rtl.conf /etc/modprobe.d/
##
# Install new splash screens
##
sudo cp splash.png splash_sad.png /usr/
##
# Auto backup camera
##
echo "[INSTALL] Reboot now!"
