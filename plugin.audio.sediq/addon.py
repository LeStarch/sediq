import sys
import xbmcgui
import xbmcplugin
import urlparse

'''
@author lestarch

A plugin to play radio stations within Kodi
'''

STATIONS = {"KOST":103.5e6,"KPCC":89.3e6,"KUSC":91.5e6,"KIIS":102.7e6}

def buildInterface(handle,stations):
    '''
    Build interface for this plugin
    @param handle - plugin handle
    @param stations - stations available for tuning
    '''
    for station,freq in stations.items():
        li = xbmcgui.ListItem("{0} - {1} MHz FM".format(station,str(freq/1e6)), iconImage='icon.png')
        xbmcplugin.addDirectoryItem(handle=handle,url="http://127.0.0.1:5000/play?freq={0}".format(freq), listitem=li)
    li = xbmcgui.ListItem("Stop Radio", iconImage='icon.png')
    xbmcplugin.addDirectoryItem(handle=handle,url="http://127.0.0.1:5000/stop", listitem=li)        
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
    buildInterface(handle, STATIONS)
    