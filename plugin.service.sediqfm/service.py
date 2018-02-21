import os
import time
import subprocess
import xbmc
'''
@author lestarch

A service to run rtl_fm_streamer
'''
def run():
    '''
    Runs the streaming program
    '''
    subprocess.call(os.path.join(os.path.dirname(__file__),
                    "resources/bin/rtl_fm_streamer.start"))
def kill():
    '''
    Kill the streamer
    '''
    subprocess.call(["pkill","rtl_fm_streamer"])


if __name__ == '__main__':
    '''
    Starts the main program
    '''
    run()
    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        # Sleep/wait for abort for 10 seconds
        if monitor.waitForAbort(10):
            break
    kill()
