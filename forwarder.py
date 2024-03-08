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

        self.client = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
        self.client.bind(('', self.serverport))

        self.recieve = threading.Thread(target=self.getClient_input)
        self.recieve.daemon = True
        self.recieve.start()

        self.send = threading.Thread(target=self.relay)
        self.send.daemon = True
        #self.send.start()

    def getClient_input(self):
        while True:
            data, addr = self.client.recvfrom(self.bufferSize)
            self.receive_message(data, addr)

    def receive_message(self, message, addr):
        mainMsg = message
        print(addr)
        self.client.sendto(message,("192.168.0.128", 1410))


    def relay(self):
            print(self.mainMsg)
            self.UDPserver.sendto("hey".encode(),("localhost", 20001))
            self.UDPserver.sendto(self.mainMsg.encode(),("localhost", 20001)) #subject to change

    def centralStartup(self):
        message = "forwarder"
        tosend = pickle.dumps(message)
        self.client.sendto(tosend, ("192.168.0.128", 20001))


    def run_program(self):
        self.centralStartup()
        while True:
            data, address = self.client.recvfrom(self.bufferSize)
            #self.receive_message(data, address)

def get_local_ip(): # this method is used to resolve your own ip address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('192.255.255.254', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP    

def main():
    ip = get_local_ip()
    print(ip)
    relay = Relay()
    relay.run_program()

if __name__ == "__main__":
    print(os.name)
    main()