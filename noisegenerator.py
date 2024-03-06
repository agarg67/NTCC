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
    serverport= 1410
    bufferSize = 4096
    mainMsg = ""
    ipList = []
    portList = []
    

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


    def getUDPserver_input(self):
        while True:
            data, addr = self.UDPserver.recvfrom(self.bufferSize)
            self.receive_message(data, addr)

    def send(self):
        print("work")

    def receive_message(self, message, addr):
        mainMsg = message
        print("hey")
        for i in range(len(self.portList)):
            try:
                self.UDPserver.sendto(message,("192.168.0.128", self.portList[i]))
            except ConnectionResetError:
                pass


    def randIP(self):
        for i in range (0, 20):
            port = random.randrange(1000, 30000)
            #print(ip)
            self.portList.append(port)
            print(self.portList[i])

        self.portList.append(20001)


    def run_program(self):
        self.randIP()
        #self.ipList.append("192.168.0.128")
        while True:
            try:
                data, address = self.UDPserver.recvfrom(self.bufferSize)
            except ConnectionResetError:
                pass

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
