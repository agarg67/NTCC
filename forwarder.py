import queue
import sys
import os
import socket
import re
import pickle
import random
import threading
import time


class Relay:
    server=""
    serverport=9999
    bufferSize = 4096
    mainMsg = ""
    client = []
    

    def __init__(self):
        self.recieve = None
        self.send = None
        self.createSocket()

    def createSocket(self):

        self.UDPserver = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
        self.UDPserver.bind(('', self.serverport))

        self.recieve = threading.Thread(target=self.getUDPserver_input)
        self.recieve.daemon = True
        self.recieve.start()

        self.send = threading.Thread(target=self.relay)
        self.send.daemon = True
        #self.send.start()

    def getUDPserver_input(self):
        while True:
            data, addr = self.UDPserver.recvfrom(self.bufferSize)
            self.receive_message(data, addr)

    def receive_message(self, message, addr):
        try:
            mainMsg = message.decode()
            print(message.decode())
            self.UDPserver.sendto(mainMsg.encode(),("localhost", 20001))
        except:
            pass

    def relay(self):
            print(self.mainMsg)
            self.UDPserver.sendto("hey".encode(),("localhost", 20001))
            self.UDPserver.sendto(self.mainMsg.encode(),("localhost", 20001)) #subject to change


    def run_program(self):
        while True:
            data, address = self.UDPserver.recvfrom(self.bufferSize)
            self.receive_message(data, address)

def main():
    relay = Relay()
    relay.run_program()

if __name__ == "__main__":
    print(os.name)
    main()