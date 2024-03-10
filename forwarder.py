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

    centralKey = None

    def __init__(self):
        self.recieve = None
        self.send = None
        self.publicKey, self.private = rsa.newkeys(1024)
        self.createSocket()

    def createSocket(self):

        self.client = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
        self.client.bind(('', self.serverport))

    def message_identifier(self, data):
        message_identifier = data.split(b" <")
        return message_identifier[0]

    def main_message(self, data):
        main_message = data.split(b" <")
        main_message[1] = main_message[1].replace(b">", b"")
        return main_message[1]

    def message_sender(self, data):
        message_sender = data.split(b" <")
        message_sender[2] = message_sender[2].replace(b">", b"")
        return message_sender[2]

    def parse_message(self, data, addr):
        
        serverIP = self.get_local_ip().encode()
        pubkey = self.publicKey.save_pkcs1()
        source = addr[0].encode()

        print("This is the data received: {}".format(data))
        print("\nThis is the data received from: {}".format(addr))
        
        if(b"ackforwarder" in data):
            identifier_flag = self.message_identifier(data)
            message_content = self.main_message(data)
            message_sender = self.message_sender(data)

        if identifier_flag == b"ackforwarder":
            self.centralKey = rsa.PublicKey.load_pkcs1(message_content.decode())
            message = b"hey" + b" <" + rsa.encrypt(b"hey", self.centralKey) + b">"+ b" <" + serverIP + b">"
            self.client.sendto(message, ("192.168.0.128", 20001))
            print(message)
        else:
            print("Message not recognized")
            return None    

    def centralStartup(self):
        serverIP = self.get_local_ip().encode()
        pubkey = self.publicKey.save_pkcs1()
        send = b"forwarder" + b" <" + pubkey + b">"+ b" <" + serverIP + b">"
        try:
            self.client.sendto(send, ("192.168.0.128", 20001))
            print(send)
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

    def get_local_ip(self): # this method is used to resolve your own ip address
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

    def run_program(self):
        self.centralStartup()
        while True:
            try:
                data, address = self.client.recvfrom(self.bufferSize)
                self.parse_message(data, address)
            except ConnectionResetError:
                print("no connections available")

##########################################################################################################################  

def main():
    #ip = get_local_ip()
    #print(ip)
    relay = Relay()
    relay.run_program()

if __name__ == "__main__":
    print(os.name)
    main()