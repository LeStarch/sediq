"""
addon.py:

Code required to launch the rtl-gst shell scipt and display it as part of OSMC/KODI. It will take input from the user
and use that input to call the system.

@author lestarch
"""
from __future__ import division
import os
import re
import sys
import copy
import json
import urllib

import urlparse
import xbmc
import xbmcgui
import xbmcplugin

from radio.handler import send_new_frequency

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
ICON=os.path.join(os.path.dirname(__file__), "icon.png")
STATIONS_FILE = os.path.join(os.path.expanduser("~"), ".kodi", "sediq.json")
GST_URL="tcp://localhost:4953"

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


def save_stations(stations):
    """
    Saves known stations from the default mixed with any stations known in the JSON file.
    :param stations: dictionary of name to freq in HZ of the station
    """
    try:
        with open(STATIONS_FILE, "w") as file_handle:
            json.dump(stations, file_handle)
    except IOError as ioe:
        xbmc.log("Failed to save stations file: {} with error: {}".format(STATIONS_FILE, ioe), level=xbmc.LOGWARNING)


def display():
    """
    Displays all known stations as part of the Kodi/OSMC interface.
    """
    for station, freq in load_stations().items():
        human_freq = "{0:.1f}".format(freq / 1e6)
        li = xbmcgui.ListItem("{0} - {1} MHz FM".format(station, human_freq), iconImage=ICON, thumbnailImage=ICON)
        li.setProperty('fanart_image', ICON)
        li.setProperty("IsPlayable","true")
        li.setInfo(type='Music', infoLabels={"Title": station + " - " + str(human_freq)})
        xbmcplugin.addDirectoryItem(handle=__handle__, url="{}?{}".format(__url__, urllib.urlencode({"action": "play", "freq": int(freq)})),
                                    listitem=li, isFolder=False)
    li = xbmcgui.ListItem("Input Station", iconImage=ICON, thumbnailImage=ICON)
    li.setProperty('fanart_image', ICON)
    li.setProperty("IsPlayable","true")
    li.setInfo(type='Music', infoLabels = {"Title": "Input Station"})
    xbmcplugin.addDirectoryItem(handle=__handle__, url="{}?{}".format(__url__, urllib.urlencode({"action": "new"})),
                                listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(__handle__)


def play(freq):
    """
    First, run the script to start the streaming server and then attempt to plat the known URL. This is done by creating
    an artificial play URL and pass it into the OSMC/Kodi for playing.
    :param freq: frequency to play
    """
    xbmc.log("Setting RTL-GST pipeline to: {} Hz".format(freq), level=xbmc.LOGINFO)
    with open("/tmp/radio-handle", "w") as file_handle:
        print(f"{freq}", file=file_handle)
    xbmc.log("Attempting to load: {}".format(GST_URL), level=xbmc.LOGINFO)
    # Playable item of GST_URL. See: (https://github.com/romanvm/plugin.video.example/blob/master/main.py:206)
    play_item = xbmcgui.ListItem(path=GST_URL)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(__handle__, True, listitem=play_item)


def enter():
    """ Allow users to enter in a new frequency

    Displays a dialog box allowing the user to enter a radio frequency of the form ###.# and must fit within the FM
    bands 88 - 108. These numbers will be expanded to megahertz afterward.
    """
    reg = re.compile(r"\d{2,3}.\d")
    station = "nonsense"
    while station != "" and not reg.match(station):
        station = xbmcgui.Dialog().input("FM Freq (MHz):", "102.7", xbmcgui.INPUT_ALPHANUM)
        if not reg.match(station) or float(station) > 108 or float(station) < 88:
            xbmcgui.Dialog().ok(
                "[ERROR] Invalid frequency",
                f"{station} is invalid. Please enter a number in the range: 88 MHz - 108 MHz"
            )
    # User canceled
    if station == "":
        return
    freq = int(float(station) * 1e6)
    name = xbmcgui.Dialog().input("Name (Optional):", "WEBN", xbmcgui.INPUT_ALPHANUM)
    name = f"{station} MHz" if name == "" else name
    stations = load_stations()
    stations[name] = freq
    xbmc.log("Saving stations: {}".format(stations), level=xbmc.LOGINFO)
    save_stations(stations)
    display()


def route():
    """
    Parses the URL and then routes the input based upon it.
    """
    parsed = dict(urlparse.parse_qsl(__params__[1:]))
    if parsed and parsed["action"] == "play":
        play(parsed["freq"])
    elif parsed and parsed["action"] == "new":
        enter()
    else:
        display()

if __name__ == "__main__":
    """
    Main program.  Hi Lewis!!!
    """
    xbmcplugin.setContent(__handle__, "audio")
    route()

