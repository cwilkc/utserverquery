from utserverquery.unrealserver import UnrealServer
from pprint import pprint
import re
import time
import socket

# Setup Logger
import logging
logger = logging.getLogger('poller')

logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(
    logging.Formatter(
        '%(name)s:%(levelname)s:%(message)s'
    )
)

logger.addHandler(stream_handler)

start = time.perf_counter()

server = UnrealServer('127.0.0.1', 7778, logger=logger)

try:
    server.poll_server()
except socket.timeout:
    print(f'{server.ip}:{server.port} did not respond.')

pprint(server.info)

finish = time.perf_counter()

print(f'Finished in {round(finish-start, 2)} second(s)')
