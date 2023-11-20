import sys
import os
import socket
import re
import pickle
import random
import threading
import time

class IP_mapper:
    ip_address1=""
    ip_address2=""
    port1=0
    port2=0
    
    def __init__(self, ip1, ip2, p1, p2):
        self.ip_address1=ip1
        self.ip_address2=ip2
        self.port1=p1
        self.port2=p2

class Forwarder:
    HOST = ""
    PORT = 0

    bufferSize = 4096
    def __init__(self):
        pass

    def forwarder(self, source, destination):
        while True:
            data = source.recv(self.bufferSize)
            if not data:
                break
            destination.sendall(data)

    def startPortForward(self, localPort, remoteHost, remotePort):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('localHost', localPort))
        server.listen(1)
        print("forwarding from localHost {localPort} to {remoteHost}: {remotePort}")


        while True:
            localSocket, localAddr = server.accept()

            print("accepted connection")

            remoteSocket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
            remoteSocket.connect(('localhost', remotePort))

            forwardRemote = threading.Thread(target = self.forwarder, args = (localSocket, remoteSocket))
            forwardlocal = threading.Thread(target = self.forwarder, args = (remoteSocket, localSocket))

            forwardRemote.start()
            forwardlocal.start()


    if __name__ == "__main__":
        localPort = 8080
        remoteHost = "example.com"
        remotePort = 9090
        message = "hi "
        startPortForward(localPort, remoteHost, remotePort)