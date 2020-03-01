from utserverquery.unrealserver import UnrealServer
import socket
from pprint import pprint
import re
import time

start = time.perf_counter()

server = UnrealServer('127.0.0.1', 7778)

server.get_info()

pprint(server.info)

finish = time.perf_counter()

print(f'Finished in {round(finish-start, 2)} second(s)')