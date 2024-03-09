import queue
import sys
import os
import socket
import re
import pickle
import random
import threading
import time
import rsa


class Relay:
    server=""
    serverport=9999
    bufferSize = 4096
    mainMsg = ""
    ipList = []
    publickey = None
    private = None

    def __init__(self):
        self.recieve = None
        self.send = None
        self.publicKeySelf, self.privatekeySelf = rsa.newkeys(1024)
        self.createSocket()

    def createSocket(self):

        self.client = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
        self.client.bind(('', self.serverport))

        """self.recieve = threading.Thread(target=self.getClient_input)
        self.recieve.daemon = True
        self.recieve.start()"""

    def parse_message(self, data, addr):
        
        print("This is the data received: {}".format(data))
        print("\nThis is the data received from: {}".format(addr))


        message_identifier = data.split(b" <")

        print(message_identifier)

        if message_identifier[0] == b"ackreceiveipmapper":
            message_identifier[1] = message_identifier[1].replace(b">", b"")
            print(message_identifier[1])
            print(message)
        else:
            print("Message not recognized")
            return None    

    def centralStartup(self):
        message = "forwarder"
        tosend = pickle.dumps(message)
        send = b"centralconnect" + b" <" + tosend + b">"
        try:
            self.client.sendto(tosend, ("192.168.0.128", 20001))
        except ConnectionResetError:
           print("centralserver is offline") 

    #Ip Map
    ################################################################################################################################
    def ipMap(self, ips):
        ipList.append("")


    #Forward Client Messages
    ################################################################################################################################

    """def getClient_input(self):
        while True:
            data, addr = self.client.recvfrom(self.bufferSize)
            self.receive_message(data, addr)"""


    def receive_message(self, message, addr):
        mainMsg = message
        print(addr)
        self.client.sendto(message,("192.168.0.128", 1410))

    def run_program(self):
        self.centralStartup()
        while True:
            try:
                data, address = self.client.recvfrom(self.bufferSize)
                self.parse_message(data, address)
            except ConnectionResetError:
                print("no connections available")

##########################################################################################################################

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