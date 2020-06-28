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
import subprocess

import urlparse
import xbmc
import xbmcgui
import xbmcplugin

# Basic Inputs avaliable at every run
__url__ = sys.argv[0]
__handle__ = int(sys.argv[1])
__params__ = sys.argv[2]

# Stations to load as default
STATIONS = {
    "KOST": 103.5e6,
    "KPCC": 89.3e6,
    "KUSC": 91.5e6,
    "KIIS": 102.7e6
}
STATIONS_FILE = os.path.join(os.path.expanduser("~"), ".kodi", "sediq.json")
GST_URL="tcp://127.0.0.1:4934"

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


def display():
    """
    Displays all known stations as part of the Kodi/OSMC interface.
    """
    for station, freq in load_stations().items():
        li = xbmcgui.ListItem("{0} - {1} MHz FM".format(station, freq // 1e6), iconImage='icon.png')
        li.setProperty("IsPlayable","false")
        li.setInfo(type = 'Music', infoLabels = {"Title": station + " - " + str(freq // 1e6)})
        xbmcplugin.addDirectoryItem(handle=__handle__, url="{}?action=play&freq={}".format(__url__, freq),
                                    listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(__handle__)


def play(freq):
    """
    First, run the script to start the streaming server and then attempt to plat the known URL. This is done by creating
    an artificial play URL and pass it into the OSMC/Kodi for playing.
    :param freq: frequency to play
    """
    subprocess.call([os.path.join(os.path.dirname(__file__), "rtl-gst", freq)])
    # Playable item of GST_URL. See: (https://github.com/romanvm/plugin.video.example/blob/master/main.py:206)
    play_item = xbmcgui.ListItem(path=GST_URL)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(__handle__, True, listitem=play_item)

def route():
    """
    Parses the URL and then routes the input based upon it.
    """
    parsed = dict(urlparse.parse_qsl(__params__[1:]))
    if parsed and parsed["action"] == "play":
        play(parsed["freq"])
    else:
        display()

if __name__ == "__main__":
    """
    Main program.  Hi Lewis!!!
    """
    xbmc.log("Sediq run with: >{}< >{}< >{}< ".format(__handle__, __url__, __params__), level=xbmc.LOGINFO)
    xbmcplugin.setContent(__handle__, "audio")
    route()

