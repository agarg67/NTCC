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
import time
import json



class Forwarder:
    centralServerIp = "192.168.97.224"
    centralPort = 20001
    ip = "192.168.216.165"
    noiseList = [("192.168.97.36", 1410), ("192.168.97.36", 3784), ("192.168.97.36", 8473)]
    noise = None

    server=""
    serverport=9999
    bufferSize = 4096
    mainMsg = ""
    ipList = []

    centralKey = None
    clusterKeyList = []
    clusterkey = None
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

    def client_message(self, data):
        main_message = data.split(b" <")
        main_message[1] = main_message[1][:len(main_message[1])-1]
        return main_message[1]

    def message_sender(self, data):
        message_sender = data.split(b" <")
        message_sender[2] = message_sender[2].replace(b">", b"")
        return message_sender[2]

    def parse_message(self, data, addr):
        
        serverIP = self.get_local_ip().encode()
        pubkey = self.publicKey.save_pkcs1()
        source = addr[0].encode()

        identifier_flag = None

        if (b"ackforwarder" in data) or (b"ackcluster" in data):
            identifier_flag = self.message_identifier(data)
            message_content = self.main_message(data)
            message_sender = self.message_sender(data)
        
        if b"sendmessage" in data:
            identifier_flag = self.message_identifier(data)
            message_content = self.client_message(data)
            print("Client message recieved")
            message_sender = self.message_sender(data)

        if identifier_flag == b"ackforwarder":
            self.centralKey = rsa.PublicKey.load_pkcs1(message_content.decode())
            print("Central Server connected")
            message = b"sendipmapper <Central_Server598135_4123.512356> <" + serverIP + b">"
            encrypted_message = rsa.encrypt(message, self.centralKey)

        elif identifier_flag == b"ackcluster":    
            
            self.clusterkey = rsa.PublicKey.load_pkcs1(message_content.decode())
            if addr[1] == 1410:
                self.clusterkey1 = self.clusterkey
                print("Noise 1 connected")
            if addr[1] == 3784:
                self.clusterkey2 = self.clusterkey
                print("Noise 2 connected")
            if addr[1] == 8473:
                self.clusterkey3 = self.clusterkey
                print("Noise 3 connected")

            
        elif identifier_flag == b"sendmessage":
            print("Forwarding message")
            self.forward_message(message_content, addr)
            

        else:
            # possibly encrypted message which needs to be decrypted
            ciphertext = data
            decrypted_messsage = rsa.decrypt(ciphertext, self.private)

            identifier_flag = self.message_identifier(decrypted_messsage)
            message_content = self.main_message(decrypted_messsage)
            message_sender = self.message_sender(decrypted_messsage)

            if identifier_flag == b"ackipmapper":

                temp = json.loads(message_content.decode())
                self.ipMap(temp)
            else:
                print("nothing yet")

    def centralStartup(self):
        serverIP = self.get_local_ip().encode()
        pubkey = self.publicKey.save_pkcs1()
        send = b"forwarder" + b" <" + pubkey + b">"+ b" <" + serverIP + b">"
        try:
            self.client.sendto(send, (self.centralServerIp, 20001))
        except ConnectionResetError:
           print("centralserver is offline") 

    #Ip Map
    ################################################################################################################################
    def ipMap(self, ips):

        self.ipList = ips
        for i in range(len(self.noiseList)):
            if self.noiseList[i][1] == 1410:
                newaddr = self.noiseList[i]
                self.clusterSend(self.clusterkey1, newaddr)
            elif self.noiseList[i][1] == 3784:
                newaddr = self.noiseList[i]
                self.clusterSend(self.clusterkey2, newaddr)
            elif self.noiseList[i][1] == 8473:
                newaddr = self.noiseList[i]
                self.clusterSend(self.clusterkey3, newaddr)

    def clusterInit(self):
        serverIP = self.get_local_ip().encode()
        pubkey = self.publicKey.save_pkcs1()
        send = b"cluster" + b" <" + pubkey + b">"+ b" <" + serverIP + b">"
        try:
            for i in range(len(self.noiseList)):
                self.client.sendto(send, self.noiseList[i])
        except ConnectionResetError:
           print("centralserver is offline") 

    def clusterSend(self, key, addr):

        serverIP = self.get_local_ip().encode()
        #until i recieve clients ip and port
        #temp = json.dumps(self.ipList).encode('utf-8')
        temp = json.dumps(self.ipList).encode('utf-8')
        ###################
        message = b"destination <" + temp + b">" + b" <" + serverIP + b">"
        encryptMsg = rsa.encrypt(message, key)
        self.client.sendto(encryptMsg, addr)



    #Forward Client Messages
    ################################################################################################################################




    def forward_message(self, message, addr):
        
        ranFlag = ["False", "False", "False"]
        trueflag = random.randrange(len(ranFlag))
        ranFlag[trueflag] = "True"
        ip = self.get_local_ip().encode()

        for i in range(len(self.noiseList)):
            fmessage = b"forwardedMessage" + b" <" + message + b">" + b" <" + str(addr[1]).encode() + b">" + b" <" + ranFlag[i].encode() + b">" 
            self.client.sendto(fmessage,(self.noiseList[i]))


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
        ip = self.get_local_ip()
        print(ip)
        self.centralStartup()
        time.sleep(3)
        self.clusterInit()

        while True:
            try:
                data, address = self.client.recvfrom(self.bufferSize)
                self.parse_message(data, address)
            except ConnectionResetError:
                print("no connections available")

##########################################################################################################################  

def main():
    forwarder = Forwarder()
    forwarder.run_program()

if __name__ == "__main__":
    print(os.name)
    main()