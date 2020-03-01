from utserverquery.unrealmaster import UnrealMasterServer
import socket
from pprint import pprint
import re
import time

start = time.perf_counter()

master = UnrealMasterServer('utmaster.epicgames.com', 28900)

master.get_servers()

master.poll_now()

servers = master.search_servers('face')

for server in servers:
    pprint(server.info)

finish = time.perf_counter()

print(f'Finished in {round(finish-start, 2)} second(s)')