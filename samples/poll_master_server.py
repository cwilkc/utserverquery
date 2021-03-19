from utserverquery.unrealmaster import UnrealMasterServer
import socket
from pprint import pprint
import re
import time

# Setup Logger
import logging
logger = logging.getLogger('poller')

logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(
    logging.Formatter(
        '%(message)s'
    )
)

logger.addHandler(stream_handler)

start = time.perf_counter()

master = UnrealMasterServer('utmaster.epicgames.com', 28900, logger=logger)

master.get_servers()

master.poll_now()

servers = master.search_servers('face')

for server in servers:
    pprint(server.info)

finish = time.perf_counter()

print(f'Finished in {round(finish-start, 2)} second(s)')