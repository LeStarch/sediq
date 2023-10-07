#!/bin/sh
# From: https://learn.adafruit.com/adding-a-real-time-clock-to-raspberry-pi/set-rtc-time
sudo update-rc.d -f fake-hwclock remove
sudo systemctl disable fake-hwclock 
sudo hwclock -w
