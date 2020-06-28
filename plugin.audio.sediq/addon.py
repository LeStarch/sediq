"""
addon.py:

Code required to launch the rtl-gst shell scipt and display it as part of OSMC/KODI. It will take input from the user
and use that input to call the system.

@author lestarch
"""
from __future__ import division
import os
import sys
import copy
import json

import xbmc
import xbmcgui
import xbmcplugin


# Stations to load as default
STATIONS = {
    "KOST": 103.5e6,
    "KPCC": 89.3e6,
    "KUSC": 91.5e6,
    "KIIS": 102.7e6
}
STATIONS_FILE = os.path.join(os.path.expanduser("~"), ".kodi", "sediq.json")


def load_stations():
    """
    Loads known stations from the default mixed with any stations known in the JSON file.
    :return: dictionary of name to freq in HZ of the station
    """
    defaults = copy.copy(STATIONS)
    try:
        with open(STATIONS_FILE, "r") as file_handle:
            saves = json.load(file_handle)
            defaults.update(saves)
    except IOError as ioe:
        xbmc.log("Failed to load stations file: {} with error: {}".format(STATIONS_FILE, ioe), level=xbmc.LOGWARNING)
    return defaults


def run(handle):
    """
    Build interface for this plugin
    :param handle - plugin handle
    :param params - parameters
    """
    for station, freq in load_stations().items():
        li = xbmcgui.ListItem("{0} - {1} MHz FM".format(station, str(freq // 1e6)), iconImage='icon.png')
        li.setProperty("IsPlayable","false")
        li.setInfo(type = 'Music', infoLabels = {"Title": station + " - " + str(freq)})
        xbmcplugin.addDirectoryItem(handle=handle, listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(handle)


if __name__ == "__main__":
    """
    Main program.  Hi Lewis!!!
    """
    plugin_url = sys.argv[0]
    plugin_handle = int(sys.argv[1])
    xbmc.log("Sediq run with: >{}< >{}< >{}< ".format(plugin_url, plugin_handle, sys.argv[2]), level=xbmc.LOGINFO)
    xbmcplugin.setContent(plugin_handle, "audio")
    run(plugin_handle)

