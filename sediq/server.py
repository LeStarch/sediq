'''
A module for controling FM radio over a server

@author: lestarch
'''
import math
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
        self.freq = 0.0
    def play(self,freq):
        '''
        Play given FM frequency
        @param freq - frequency to play
        '''
        if math.fabs(self.freq-freq) < 0.1:
            return 
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
        self.temp.terminate()
        self.process.terminate()
        for i in range(0,4):
            if not self.process.poll() is None and not self.temp.poll() is None:
                self.process = None 
                self.temp = None
                time.sleep(0.500)
                return
            time.sleep(0.250)
        self.temp.terminate()
        self.process.kill()
        self.process = None
        self.temp = None
        time.sleep(0.500)
fm = FMServer()
@app.route("/play")
def play():
    '''
    Play a request
    '''
    freq = float(request.args.get("freq"))
    fm.play(freq)
    return "Playing: {0}".format(freq)
@app.route("/stop")
def stop():
    '''
    Stop radio
    '''
    fm.stop()
    return "Stopping!"

if __name__ == '__main__':
    '''
    Run the server
    '''
    app.run(debug=True)
