# Sediq

A software-defined radio plugin for Kodi/XBMC/OSMC. With a rtl-sdr digital capable USB tuner installed, this can also play radio stations. 

*Note:* This software is in early, but functional prototype stage. Thus stations are hard-coded for the LA area, but the user can enter in
stations of their choice (and save them).

## Deathclock Warning

This code installs deathclock.service which will automatically shutdown the system after 30-32 seconds if GPIO pin 23 (8th down from top right)
fails to detect high. This is such that when the power signal is cut for ~30 seconds, an orderly shutdown may begin.

To disable this function, supply 5V to the 8th pin, or run `systemctl disable deathclock` after install.

## Installation

This depends on OSMC to run currently. This should be the base image for the RPI. Then run the following:

```
git clone https://github.com/lestarch/sediq.git
sediq/install.sh
```

**Note:** this may require administration rights.


## Boot Speed

**Untested**

Add to /boot/config.txt
```
# Boot improvements
dtoverlay=pi3-disable-bt
dtoverlay=sdtweak,overclock_50=100
boot_delay=0
```
