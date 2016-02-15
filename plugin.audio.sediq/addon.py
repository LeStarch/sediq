import sys
import xbmcgui
import xbmcplugin
import urllib
import urlparse

'''
@author lestarch

A plugin to play radio stations within Kodi
'''

STATIONS = {"KOST":103.5e6,"KPCC":89.3e6,"KUSC":91.5e6,"KIIS":102.7e6}
URL = "http://127.0.0.1:5000/"
def run(handle,stations,params):
    '''
    Build interface for this plugin
    @param handle - plugin handle
    @param stations - stations available for tuning
    @param params - parameters
    '''
    for station,freq in stations.items():
        li = xbmcgui.ListItem("{0} - {1} MHz FM".format(station,str(freq/1e6)), iconImage='icon.png')
        li.setProperty("IsPlayable","false")
        xbmcplugin.addDirectoryItem(handle=handle,url="plugin://plugin.audio.sediq/?type={0}&freq={1}".format("play",freq), listitem=li)
    li = xbmcgui.ListItem("Stop Radio", iconImage='icon.png')
    li.setProperty("IsPlayable","false")
    xbmcplugin.addDirectoryItem(handle=handle,url="plugin://plugin.audio.sediq/?type=stop", listitem=li)        
    xbmcplugin.endOfDirectory(handle)
    if not params.get("type",None) is None:
        url = "{0}{1}?freq={2}".format(URL,params.get("type",["stop"])[0],params.get("freq",[0.0])[0])
        urllib.urlopen(url).close()
        
def processQuery(query):
    '''
    Process the query string
    @param query - query string
    '''
    return urlparse.parse_qs(query.strip("?"))

if __name__ == "__main__":
    '''
    Entry point for this plugin
    '''
    purl = sys.argv[0]
    handle = int(sys.argv[1])
    xbmcplugin.setContent(handle, 'audio')
    params = processQuery(sys.argv[2])
    run(handle, STATIONS,params)
    