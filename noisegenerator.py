import sys
import os
import socket
import re
import pickle
import random
import threading
import time


class NoiseGenerator:
    HOST = ""
    PORT = 0

    bufferSize = 4096
    def __init__(self):
        pass

    def forwarder(source, destination):
        while True:
            data = source.recv(bufferSize)
            if not data:
                break
            destination.sendall(data)

    def startPortForward(localPort, remoteHost, remotePort):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('localHost', localPort))
        server.listen(1)
        print("forwarding from localHost {localPort} to {remoteHost}: {remotePort}")


        while True:
            localSocket, localAddr = server.accept()

            print("accepted connection")

            remoteSocket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
            remoteSocket.connect(('localhost', remotePort))

            forwardRemote = threading.Thread(target = forwarder, args = (localSocket, remoteSocket))
            forwardlocal = threading.Thread(target = forwarder, args = (remoteSocket, localSocket))

            forwardRemote.start()
            forwardlocal.start()


    if __name__ == "__main__":
        localPort = 8080
        remoteHost = "example.com"
        remotePort = 9090
        message = "hi "
        startPortForward(localPort, remoteHost, remotePort)