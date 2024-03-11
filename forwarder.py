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

import json



class Relay:
    server=""
    serverport=9999
    bufferSize = 4096
    mainMsg = ""
    ipList = []
    ranFlag = [False, False, False]

    centralKey = None
    clusterkey1 = None
    clusterkey2 = None
    clusterkey3 = None

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

        print("This is the data received: {}\n".format(data))
        print("\nThis is the data received from: {}\n".format(addr))

        identifier_flag = None

        if (b"ackforwarder" in data) or (b"ackcluster" in data):
            identifier_flag = self.message_identifier(data)
            message_content = self.main_message(data)
            message_sender = self.message_sender(data)

        if identifier_flag == b"ackforwarder":
            self.centralKey = rsa.PublicKey.load_pkcs1(message_content.decode())

            message = b"sendipmapper <Central_Server598135_4123.512356> <" + serverIP + b">"

            print(message)

            encrypted_message = rsa.encrypt(message, self.centralKey)
            print(encrypted_message)

            self.client.sendto(encrypted_message, addr)
        elif identifier_flag == b"ackcluster":
            if(self.clusterkey1 == None):
                self.clusterkey1 = rsa.PublicKey.load_pkcs1(message_content.decode())
                print(self.clusterkey1)
            elif(self.clusterkey2 == None):
                self.clusterkey2 = rsa.PublicKey.load_pkcs1(message_content.decode())
            else:
                self.clusterkey3 = rsa.PublicKey.load_pkcs1(message_content.decode())
            self.clusterSend()
            

        else:
            # possibly encrypted message which needs to be decrypted
            ciphertext = data
            decrypted_messsage = rsa.decrypt(ciphertext, self.private)

            identifier_flag = self.message_identifier(decrypted_messsage)
            message_content = self.main_message(decrypted_messsage)
            message_sender = self.message_sender(decrypted_messsage)

            if identifier_flag == b"ackipmapper":
                print("This is the message content: {}".format(message_content))
                print("This is the message sender: {}".format(message_sender))

                temp = json.loads(message_content.decode())
                self.ipMap(temp)
                self.sendM()
                print(temp)
            elif identifier_flag == b"cluster":
                print("This is the message content: {}".format(message_content))
                print("This is the message sender: {}".format(message_sender))
            else:
                print("nothing yet")



            






            #message = b"hey" + b" <" + rsa.encrypt(b"hey", self.centralKey) + b">"+ b" <" + serverIP + b">"
            #self.client.sendto(message, ("192.168.0.128", 20001))
            #print(message)
        #else:
        #    print("Message not recognized")
        #    return None

    def centralStartup(self):
        serverIP = self.get_local_ip().encode()
        pubkey = self.publicKey.save_pkcs1()
        send = b"forwarder" + b" <" + pubkey + b">"+ b" <" + serverIP + b">"
        try:
            self.client.sendto(send, ("172.20.10.9", 20001))
        except ConnectionResetError:
           print("centralserver is offline") 

    #Ip Map
    ################################################################################################################################
    def ipMap(self, ips):
        ipList = []
        ipList = ips
        print(ipList[0])

    def clusterInit(self):
        serverIP = self.get_local_ip().encode()
        pubkey = self.publicKey.save_pkcs1()
        send = b"cluster" + b" <" + pubkey + b">"+ b" <" + serverIP + b">"
        try:
            self.client.sendto(send, ("10.159.233.223", 1410))
        except ConnectionResetError:
           print("centralserver is offline") 

    def clusterSend(self):
        serverIP = self.get_local_ip().encode()
        #until i recieve clients ip and port
        temp = json.dumps(("10.159.233.223", 9999)).encode('utf-8')
        ###################
        print(temp)
        message = b"destination <" + temp + b">" + b" <" + serverIP + b">"
        encryptMsg = rsa.encrypt(message, self.clusterkey1)
        print(encryptMsg)
        self.client.sendto(encryptMsg, ("10.159.233.223", 1410))



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
        self.clusterInit()
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