import socket
from pprint import pformat

from pdb import set_trace as st

# Setup Logger
import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

class UnrealServer(object):
    
    def __init__(
        self,
        ip,
        port,
        **kwargs,
    ):
        """
            UnrealServer class init statement

            Args:
                ip (str): Resolvable DNS name or IP address for the
                    Master Server you'd wish to poll.
                port (int): The port number listening for server queries
        """

        self.ip = ip
        self.port = port

        self.info = {
            'ip_address': ip,
            'query_port': port,
        }

        if 'logger' not in kwargs:
            self.logger = logger
        else:
            self.logger = kwargs['logger']

        if 'timeout' not in kwargs:
            self.timeout = 5
        else:
            self.timeout = kwargs['timeout']

        self.logger.debug(f'Passed kwargs: {kwargs}')

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(self.timeout)
        self.server = (self.ip, self.port)


    def __str__(self):

        return f"{self.title} - {self.ip}:{self.port}"


    @property
    def title(self):

        try:
            return self.info['hostname']
        except KeyError:
            return None


    @property
    def has_xserver_query(self):

        if 'XServerQuery' in self.info:
            return True
        else:
            return False


    def get_data(
        self,
        command,
        use_xserver_query=True,
    ):
        """
            Poll the server for the information header and apply to the class
            attribute of 'info'

            Kwargs:
                use_xserver_query (bool): Append xserverquery to the command
                automatically. This shouldn't affect a vanilla server.
                XServerQuery module (tested against v2.0.1) provides a lot
                more server detail about current match, players and score.
                Pass False if it causes issues with any other ServerActor
                replacement libraries.

            Returns: None
        """

        if use_xserver_query:
            command += '\\xserverquery'

        self.logger.debug(
            f'Sending command \'\\{command}\\\' to {self.ip}:{self.port}'
        )

        self.sock.sendto(str.encode(f"\\{command}\\"), self.server)

        data = []

        while True:
            
            msg, _ = self.sock.recvfrom(4096)

            self.logger.debug(f'Raw data received:\n{msg}\n')

            try:
                data.extend(msg.decode('utf-8').split('\\')[1:-2]) 
            except UnicodeDecodeError:
                return

            if msg.split(b'\\')[-2] == b'final':
                break

        elements = zip(data[::2], data[1::2])

        for el in elements:
            self.info[el[0]] = el[1]


    def get_server_info(
        self,
    ):

        self.get_data('info')


    def get_server_players(
        self,
    ):

        self.get_data('players')


    def get_server_rules(
        self,
    ):

        self.get_data('rules')


    def poll_server(
        self
    ):

        self.logger.info(f'Polling server: {self.ip}:{self.port} {self.title or ""}')

        try:
            self.get_data('status')
        except socket.timeout:
            self.logger.debug(
                f'Timeout ({self.timeout} seconds) receiving data from '
                f'{self.ip}:{self.port}'
            )

            raise socket.timeout

        self.logger.debug(f'Server object built:\n{pformat(self.info)}')
        self.logger.info(f'Server {self} built.')