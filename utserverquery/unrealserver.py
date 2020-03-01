import socket

class UnrealServer(object):
    
    def __init__(
        self,
        hostname,
        port,
        timeout=5,
    ):
        """
            UnrealServer class init statement

            Args:
                hostname (str): Resolvable DNS name or IP address for the
                    Master Server you'd wish to poll.
                port (int): The port number listening for server queries
        """

        self.hostname = hostname
        self.port = port
        self.info = {}

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout)
        self.server = (self.hostname, self.port)

    def get_info(self):
        """
            Poll the server for the information header and apply to the class
            attribute of 'info'

            Returns: None
        """
        
        command = b'\\info\\'

        self.sock.sendto(command, self.server)

        try:
            msg, _ = self.sock.recvfrom(4096)
        except socket.timeout:
            return

        try:
            data = msg.decode('utf-8').split('\\')[1:-2]
        except UnicodeDecodeError:
            return

        elements = zip(data[::2], data[1::2])

        for el in elements:
            self.info[el[0]] = el[1]

        