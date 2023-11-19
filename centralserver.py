import sys
import os
import socket
import re
import pickle
import random
import threading
import time

# Parameters that will be used to connect to the central server
localPort = 7823
bufferSize = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class CentralServer:
    def fetch_ip_address(self):
        ip_address = ''
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address

    def __init__(self):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(('', localPort))
        print("Central Server Initialized : {}:{}".format(self.fetch_ip_address(), localPort))

    def main(self):
        while True:
            data, addr = sock.recvfrom(bufferSize)
            print("received message: {} from {}".format(data, addr))
            sock.sendto("received OK", addr)

if __name__ == "__main__":
    centralServer = CentralServer()
    centralServer.__init__()
    centralServer.main()
