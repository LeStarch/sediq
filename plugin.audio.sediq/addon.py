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
URL = "http://127.0.0.1:2346/{0}/1"
def run(handle,stations,params):
    '''
    Build interface for this plugin
    @param handle - plugin handle
    @param stations - stations available for tuning
    @param params - parameters
    '''
    for station,freq in stations.items():
        li = xbmcgui.ListItem("{0} - {1} MHz FM".format(station,str(freq/1e6)), iconImage='icon.png')
        li.setProperty("IsPlayable","true")
        li.setInfo(type = 'Music', infoLabels = {"Title": station+" - "+str(freq)})
        xbmcplugin.addDirectoryItem(handle=handle,url=URL.format(int(freq)), listitem=li,isFolder=False)
    xbmcplugin.endOfDirectory(handle)

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

