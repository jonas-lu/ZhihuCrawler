import sys
import os
import logging
import signal
import slave
import master
import config

mode = sys.argv[1]
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(CURRENT_DIR))

fmt = "%(asctime)s %(name)s %(message)s"
logging.basicConfig(level=logging.WARNING, format=fmt)


def on_term_handler(sig, frame):
    logging.warning('Recv SIGTERM')
    if mode == "slave":
        slave.terminate()
    elif mode == "master":
        master.terminate()

signal.signal(signal.SIGTERM, on_term_handler)

config.set_config('env', 'run')
if mode:
    if mode == "master":
        master.start('jonas-lu')
    else:
        instance_id = sys.argv[2] if len(sys.argv) >= 3 else 0
        slave.start(instance_id)
else:
    sys.exit('Invalid arguments')
