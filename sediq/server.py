'''
A module for controling FM radio over a server

@author: lestarch
'''
import time
import subprocess
from flask import Flask
from flask import request

app = Flask(__name__)

class FMServer(object):
    '''
    A REST server playing 
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self.process = None
    def play(self,freq):
        '''
        Play given FM frequency
        @param freq - frequency to play
        '''
        self.stop()
        fmcmd = ["rtl_fm","-f",str(freq),"-M","fm","-s","200000","-r","48000","-"]
        playcmd = ["aplay","-r","48k","-f","S16_LE"]
        self.process = subprocess.Popen(fmcmd,stdout=subprocess.PIPE)
        #Captured as a variable to prevent GC from collecting orphaned reference
        self.temp = subprocess.Popen(playcmd,stdin=self.process.stdout)
    def stop(self):
        '''
        Stop the playback
        '''
        if self.process is None:
            return
        self.process.terminate()
        for i in range(0,4):
            if not self.process.poll() is None:
                self.process = None 
                return
            time.sleep(0.250)
        self.process.kill()
        self.process = None
        self.temp = None
fm = FMServer()
@app.route("/play")
def play():
    '''
    Play a request
    '''
    freq = float(request.args.get("freq"))
    fm.play(freq)
    return "Playing: {0}".format(freq)
@app.route("/stop/")
def stop():
    '''
    Stop request
    '''
    fm.stop()
    return "Stopping"

if __name__ == '__main__':
    '''
    Run the server
    '''
    app.run(debug=True)
