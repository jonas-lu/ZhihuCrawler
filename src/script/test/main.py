import sys
# import os
# import logging
# import signal
# from sub import Sub
#
# CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, os.path.dirname(CURRENT_DIR))
#
# fmt = "%(asctime)s %(message)s"
# logging.basicConfig(level=logging.WARNING, format=fmt)
#
#
# def on_term_handler(sig, frame):
#     logging.warning('Recv SIGTERM')
#     sub.terminate()
#
# signal.signal(signal.SIGTERM, on_term_handler)
#
# sub = Sub()
# sub.start()
# sub.join()

print(sys.argv[1], sys.argv[2])