#!/bin/sh
##
# Settings
##
KODI=/home/osmc/.kodi/userdata/
HERE=`dirname $0`
HERE=`cd ${HERE}; pwd`
##
# Sediq required packages
##
sudo apt-get install \
  build-essential \
  gcc \
  libusb-1.0-0-dev \
  libev-dev \
  cmake \
  automake \
  git \
  vim \
  gstreamer-1.0 \
  gstreamer1.0-tools \
  gstreamer1.0-plugins-base \
  gstreamer1.0-plugins-good \
  libgtk2.0-dev \
  libgstreamer1.0-dev \
  libgstreamer-plugins-base1.0-dev \
  rbp-userland-dev-osmc \
  rtl-sdr \
  gstreamer1.0-plugins-bad
##
# Update submodules
##
OCWD=`pwd`
cd ${HERE}
git submodule update --init --recursive
cd ${OCWD}
##
# WGET the source for OMX acceleration
##
wget https://gstreamer.freedesktop.org/src/gst-omx/gst-omx-1.10.4.tar.xz
tar -xJf gst-omx-1.10.4.tar.xz
cd gst-omx-1.10.4
./configure --with-omx-header-path=/opt/vc/include/IL --with-omx-target=rpi
make -j4
#sudo make install
##
# Link in the installed library
##
cd /usr/lib/arm-linux-gnueabihf/gstreamer-1.0/
sudo ln -s /usr/local/lib/gstreamer-1.0/libgstomx.so
cd ${OCWD}
##
# Aux video files
##
cd ${KODI}
ln -s ${HERE}/camera/advancedsettings.xml
cd ${OCWD}
cd  /lib/systemd/system/
sudo ln -s ${HERE}/camera/camera.service
cd ${OCWD}
##
# Add in skin, and radio plugins
##
cd /home/osmc/.kodi/addons
ln -s ${HERE}/skin.sediqskin
ln -s ${HERE}/plugin.audio.sediq
ln -s ${HERE}/plugin.service.sediqfm
cd ${OCWD}
##
# Boot options for iqcaudio
##
sudo sed -i".bak" -e 's/^\(dtoverlay.*\)/#\1/' \
                  -e 's/^\(dtparam=audio=.*\)/#\1/' \
                  -e '$ s/$/\ndtoverlay=iqaudio-dacplus,auto_mute_amp\ndtparam=audio=off/' /boot/config.txt
##
# Install the streamer 
##
pwd
git clone https://github.com/AlbrechtL/rtl_fm_streamer.git
#cd rtl_fm_streamer/
#cmake . -DCMAKE_INSTALL_PREFIX:PATH=/usr 
#make
#sudo make install
sudo cp rtl-sdr.rules /etc/udev/rules.d/99-rtl-sdr.rules
sudo cp ../blacklist-rtl.conf /etc/modprobe.d/
echo "[INSTALL] Reboot now!"
