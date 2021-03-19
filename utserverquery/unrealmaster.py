import socket
import re
import concurrent.futures
from pprint import pformat
from .unrealserver import UnrealServer

# Setup Logger
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

class UnrealMasterServer(object):
    
    def __init__(
        self,
        hostname,
        port,
        **kwargs,
    ):
        """
            UnrealMasterServer class init statement

            Args:
                hostname (str): Resolvable DNS name or IP address for the
                    Master Server you'd wish to poll.
                port (int): The port number the master server is
                    listening on
        """

        self.hostname = hostname
        self.port = port
        self.servers = []

        if 'logger' not in kwargs:
            self.logger = logger
        else:
            self.logger = kwargs['logger']

        if 'timeout' not in kwargs:
            self.timeout = 5
        else:
            self.timeout = kwargs['timeout']

        self.logger.debug(f'Passed kwargs: {kwargs}')

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.server = (self.hostname, self.port)

    def get_servers(self):
        """
            Poll the Master Server for a client list and sets the class
            attribute of 'servers' to a list of Server objects.

            Returns: None
        """

        # The Quake style queries to end clients (whether they be Master Servers
        # or server clients), need a header of 4 \xFF bytes

        command = b"\\list\\gamename\\ut\\final\\"

        self.logger.debug(
            f'Sending command \'\\{command}\\\' to {self.hostname}:{self.port}'
        )

        self.sock.connect(self.server)
        self.sock.sendto(command, self.server)

        fullmsg = ''

        try:
            while True:
                msg = self.sock.recv(4096)

                if len(msg) <= 0:
                    break

                fullmsg += msg.decode('utf-8')
        except socket.timeout as e:
            raise e

        self.logger.debug(f'Raw data received:\n\n{fullmsg}')

        data = fullmsg.split('\\')[5:]

        for item in data[1::2][:-1]:
            self.servers.append(
                UnrealServer(item.split(':')[0], int(item.split(':')[1]), logger=self.logger)
            )

        self.logger.info(
            f'Found {len(self.servers)} servers running.'
        )

    def search_servers(self, query):
        """
            Search for a given query in any of the values in the server dict
            keys.

            Args:
                query (str): the search query to look for in the dictionary keys

            Returns: A list of Servers
        """
        if not self.servers:
            return

        return_list = []

        self.logger.info(
            f'Searching {len(self.servers)} servers for keyword \'{query}\'.'
        )

        for server in self.servers:
            self.logger.info(f"Scanning {server} for keyword.")
            self.logger.debug(f"{pformat(server.info)}")

            info_results = [
                key for key, val in server.info.items() 
                if re.search(
                    query,
                    str(val),
                    re.IGNORECASE
                )
            ]

            if info_results:
                return_list.append(server)

        return return_list

    

    def poll_now(self):
        """
            Concurrently poll all servers captured from the Master Server and
            capture info and status headers.

            Returns: None
        """

        def get_server_info(server):
            server.poll_server()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(get_server_info, self.servers)