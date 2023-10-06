import os
import math
import time
import signal
import subprocess
import zmq

from pathlib import Path

FIFO=Path( "/tmp/radio-fifo")
SAMPLE_RATE = 48000
BLOCK_SIZE = 4
RADIO_ARGS = ["rtl_fm", "-M", "wbfm", "-s", "200000", "-r", str(SAMPLE_RATE), "-", "-f"]
IPC_SOCKET = "/tmp/radio-handle"

def send_new_frequency(frequency):
    """ Send a new frequency! """
    # Build a context
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"ipc://{IPC_SOCKET}")
    socket.send_string(str(int(frequency)))
    message = socket.recv_string()
    socket.close()



class RadioManager(object):
    """ Class managing radio via rtl-sdr """

    def __init__(self):
        """ Init function setting up member variables """
        self._frequency = 0.0
        self._process = None

    def frequency(self, frequency):
        """ Frequency setter and radio updater
        
        Freqncy update function that sets the radio to play a specific radio station.
        
        Args:
            frequency: new frequency as a float
        """
        if math.isclose(frequency, self._frequency, abs_tol=1e5):
            return
        self._frequency = frequency
        self.update()

    def update(self):
        """ Update the running frequency """
        print(f"[FREQ] Updating frequency to: {self._frequency}")
        # Kill previous process
        if self._process is not None:
            self._process.send_signal(signal.SIGTERM)
            self._process.wait()
        # Start new process
        self._process = subprocess.Popen(RADIO_ARGS + [str(int(self._frequency))],
                                         bufsize=0, text=False, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    def read(self):
        """ Read data from radio """
        if self._process.poll() is None:
            return self._process.stdout.read(BLOCK_SIZE)
        return b"\0" * BLOCK_SIZE

def radio_read_loop(radio: RadioManager, socket, fifo_handle):
    """ Read radio and check for changes, in a loop """
    stop = False
    total_bytes = 0
    last = time.time()
    while not stop:
        read_bytes = radio.read()
        total_bytes += len(read_bytes)
        if len(read_bytes) == BLOCK_SIZE:
            fifo_handle.write(read_bytes)

        now = time.time()
        if (now - last) >= 0.5:
            last = now
            # Check for a message
            try:
                message = socket.recv_string(flags=zmq.NOBLOCK)
                try:
                    fifo_handle.write(b"\0" * int(BLOCK_SIZE * SAMPLE_RATE * 0.5))
                    radio.frequency(int(message))
                    socket.send_string("SUCCESS")
                except:
                    socket.send_string("FAIL")
            except:
                pass
            

def main():
    """ Main program, Hi Lewis!!! """
    try:
        os.mkfifo(FIFO)
        print(f"[START] Making FIFO: {FIFO}")
        radio = RadioManager()
        
        # Build a context
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(f"ipc://{IPC_SOCKET}")

        # Open the fifo and begin the data loop
        with open(FIFO, "wb") as file_handle:
            radio.frequency(89.3e6)
            radio_read_loop(radio, socket, file_handle)
    finally:
        print(f"[STOP] Removing FIFO at: {FIFO}")
        os.remove(FIFO)
        socket.close()
        os.remove(f"{IPC_SOCKET}")


if __name__ == "__main__":
    main()
