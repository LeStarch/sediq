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
ln -fs ${HERE}/playercorefactory.xml
cd ${OCWD}
cd  /lib/systemd/system/
sudo ln -fs ${HERE}/deathclock.service
sudo ln -fs ${HERE}/radio-service/radio-service.service
sudo ln -fs ${HERE}/camera/camera.service
sudo systemctl enable deathclock
sudo systemctl enable radio-service
sudo systemctl enable camera
cd ${OCWD}
##
# Add in skin, and radio plugins
##
cd ~/.kodi/addons
ln -fs ${HERE}/skin.sediqskin
ln -fs ${HERE}/plugin.audio.sediq
cd ${OCWD}
##
# Boot options for iqcaudio and boot speed
##
##
# Install the RTL rules and modprobe setup
##
sudo cp "${HERE}/rtl-sdr.rules" /etc/udev/rules.d/99-rtl-sdr.rules
sudo cp "${HERE}/blacklist-rtl.conf" /etc/modprobe.d/
sudo cp "${HERE}/autostart" /etc/xdg/lxsession/LXDE-pi/autostart
##
# Install new splash screens
##
sudo cp splash.png splash_sad.png /usr/
##
# Auto backup camera
##
echo "[INSTALL] Reboot now!"
