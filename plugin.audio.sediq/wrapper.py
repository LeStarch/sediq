####
# wrapper.py:
#
# Wraps the rtl_gst call to supply arguments.
####
import os
import sys
GST=os.path.join(os.path.dirname(__file__), "rtl-gst")
if len(sys.argv) < 2:
    sys.exit(1)
os.system("{} {}".format(GST, sys.argv[1]))
