import argparse
import os
import math
import time
import signal
import subprocess
import select
from pathlib import Path


class RadioManager(object):
    """ Manages RTL-SDR radio via a rtl_fm subprocess
    
    Data is streamed using the rtl_fm program installed with the rtl-sdr package. This program produces a stream of U16
    sample pairs to standard out. This process intercepts that data via a pipe and writes the data to the output file
    handle. This has the adviantage that EOD/EOS tokens in the underlying stream are not passed through as would happen
    with a unix pipe. That way the output stream exists even when the underlying program is (re)started.

    Changes to the programmed frequency are read from a file and the rtl-sdr program is restarted. During this restart,
    a large block of zeros is written to the output to enusre that the output stream has no outages.
    """
    BLOCK_SIZE = (2 * 2) # 2 bytes (U16) * 2/sample

    def __init__(self, update_path: Path, output_file: Path, frequency=89.3, sample_rate=48000, update_time=0.5):
        """ Construct the radio manager class

        Sets the initial variables for the radio class. This is a context manager, so with with statement must be used
        or the __enter__ method called *before* the loop function is called.
        
        Args:
            update_path: path to update file
            output_file: path to the output file
            frequency: initial frequency to tune to
        """
        self.stop = False
        self._frequency = int((89.3 if frequency > 108 or frequency < 88 else frequency) * 1e6)
        self._process = None
        self._update_path = update_path
        self._output_file = output_file
        self._previous_update_error = False
        self._sample_rate = sample_rate
        self._radio_args = ["rtl_fm", "-M", "wbfm", "-s", "200000", "-r", str(sample_rate), "-", "-f"]
        self._update_time = update_time
        self._file_handle = None

    def __enter__(self):
        """ Enter the radio context
        
        When entering the radio context, several things are done. First, the fifo output file is created, next the
        radio is initially tuned. Within the context, the **loop* function should be called.
        """
        print(f"[START] Making FIFO: {self._output_file}")
        os.mkfifo(str(self._output_file))
        print(f"[START] Opening FIFO: {self._output_file}")
        self._file_handle = open(self._output_file, "wb")
        self._radio()
        return self

    def __exit__(self, type, value, traceback):
        """ Exit the radio context
        
        When leaving the radio context, several things are cleaned up. First, the radio process is is killed. Next,
        the output file is closed and removed.
        """
        print(f"[START] Making FIFO: {self._output_file}")
        self._radio(just_kill=True)
        try:
            self._file_handle.close()
        except:
            pass
        try:
            self._output_file.unlink()
        except:
            pass

    def update(self, frequency: int):
        """ Set the frequency when it is different from the currently set frequency
        
        Freqncy update function that sets the radio to play a specific radio station. This update is only performed
        when the new frequency differes by more than 0.1 MHz. This will internally update the radio program.
        
        Args:
            frequency: new frequency as a float
        """
        if math.isclose(frequency, self._frequency, abs_tol=1e5):
            return
        self._frequency = frequency
        self._radio()

    def _radio(self, just_kill=False):
        """ Update the radio station frequency
        
        Kills the existing radio process and starts a new process. The radio process is given 200ms to close before the
        new process is started up. When more than 200ms elapses the SIGKILL hammer is brought down upon the process
        forcing its immediate termination.

        In order to ensure that the data stream is not interrupted while this process takes place, a chuck of zero-data
        is written to the output file handle. This ensures that data is pre-queued to compensate for the switch.

        When just_kill is set, the radio process is killed and nothing more.

        Args:
            just_kill: only stop but not restart the process
        """
        print(f"[FREQ] Updating frequency to: {self._frequency}")
        if not just_kill:
            self._file_handle.write(b"\0" * int(self.BLOCK_SIZE * self._sample_rate * self._update_time))
        # Kill previous process
        if self._process is not None:
            print("[PROC] Killing previous process")
            self._process.send_signal(signal.SIGTERM)
            time.sleep(0.200)
            self._process.send_signal(signal.SIGKILL)
            self._process.wait()
        # Start new process
        if not just_kill:
            print("[PROC] Starting radio process")
            self._active_frequency = self._frequency
            self._process = subprocess.Popen(self._radio_args + [str(int(self._frequency))],
                                             bufsize=0, text=False, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    def pass_data(self):
        """ Read data from the radio program and pass it to output
        
        The radio program produces a sample pair of U16s to stdout. This will read one pait (called a block) and passes
        that data to the output file-handle. This redirection prevents an EOD being written to the output during a
        switch.

        If the process has ended as detected via a poll call, then this step is skipped to prevent issues and a zero
        block is written instead.
        """
        if self._process.poll() is None:
            self._file_handle.write(self._process.stdout.read(self.BLOCK_SIZE))
        else:
            self._file_handle.write(b"\0" * self.BLOCK_SIZE)

    def check(self):
        """ Check for frequency update request
        
        Checks the frequency file for an updated frequency. If the frequency file exists then read the frequency from
        the file and pass it to the update call.

        When there is an error or the frequency is out-of-range the previous error flag is set. If an error occurs
        twice then the file is removed and will need to be recreated.
        """
        try:
            with open(self._update_path, "r") as file_handle:
                frequency = int(file_handle.read().strip())
                if frequency <= 108e6 or frequency >= 88e6:
                    self._previous_update_error = False
                    self.update(frequency)
                else:
                    raise ValueError(frequency)
        except:
            if self._previous_update_error:
                try:
                    self._update_path.unlink()
                except:
                    pass
            else:
               self._previous_update_error = True
    
    def loop(self):
        """ Radio redirection program loop """
        assert self._file_handle is not None, "Start radio in radio context"
        last_poll_time = time.time()
        while not self.stop:
            now = time.time() 
            # Check for updates at a specific poll time
            if now >= last_poll_time + self._update_time:
                last_poll_time = now
                self.check()
            self.pass_data()


def parse_arguments():
    """ Parse the command line arguments """
    parser = argparse.ArgumentParser(description="Write FM audio sample pairs to the given output file-path")
    parser.add_argument("--sample-rate", type=int, help="Sample rate to pass to rtl_fm", default=48000)
    parser.add_argument("--output-path", type=Path, help="Path to file where output will be written",
                        default=Path("/tmp/radio-output"))
    parser.add_argument("--update-file", type=Path, help="Path to be checked for a file containing updates",
                        default=Path("/tmp/radio-update"))
    parser.add_argument("--update-time", type=float, help="Time in seconds to check for updates. May be fractional.",
                        default=0.5)
    parser.add_argument("--frequency", type=float, help="Initial frequency", default=89.3)
    return parser.parse_args()

def main():
    """ Main program, Hi Lewis!!! """
    args = parse_arguments()
    with RadioManager(args.update_file, args.output_path, args.frequency, args.sample_rate, args.update_time) as radio:
        radio.loop()


if __name__ == "__main__":
    main()
