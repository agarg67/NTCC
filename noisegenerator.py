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

class Noise:
    forwarderIP = "192.168.0.128"
    serverport= 1410
    bufferSize = 4096
    mainMsg = ""
    ipList = []
    portList = []
    forwarderPublicKey = None
    dummyIp = [("192.168.216.224", 6666), ("192.168.216.37", 5555)]
    

    def __init__(self):
        self.publicKey, self.private = rsa.newkeys(1024)
        self.createSocket()
    

    def createSocket(self):
        self.UDPserver = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
        self.UDPserver.bind(('', self.serverport))

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

    def flag(self, data):
        flag = data.split(b" <")
        flag[3] = flag[3].replace(b">", b"")
        return flag[3]

    def parse_message(self, data, addr):

        serverIP = self.get_local_ip().encode()
        pubkey = self.publicKey.save_pkcs1()
        source = addr[0].encode()

        print("This is the data received: {}".format(data))
        print("\nThis is the data received from: {}".format(addr))
        identifier_flag = None

        if(b"forwardedMessage" in data):
            identifier_flag = self.message_identifier(data)
            print(identifier_flag)
            message_content = self.client_message(data)
            message_sender = self.message_sender(data)
            flag = self.flag(data)


        if(b"cluster" in data):
            identifier_flag = self.message_identifier(data)
            message_content = self.main_message(data)
            message_sender = self.message_sender(data)

        if identifier_flag == b"cluster":
            self.forwarderPublicKey = rsa.PublicKey.load_pkcs1(message_content.decode())
            print(self.publicKey)

            message = (b"ackcluster <" + pubkey + b"> <" + serverIP + b">")
            self.UDPserver.sendto(message, addr)

        elif identifier_flag == b"forwardedMessage":
            print("it works")
            print(message_content)
            print(flag)
            if flag == b"True":
                self.sendMessage(message_content, message_sender)
            else:
                print("not the one")

        else:
            # possibly encrypted message which needs to be decrypted
            ciphertext = data
            decrypted_messsage = rsa.decrypt(ciphertext, self.private)

            identifier_flag = self.message_identifier(decrypted_messsage)
            message_content = self.main_message(decrypted_messsage)
            message_sender = self.message_sender(decrypted_messsage)

            if identifier_flag == b"destination":
                temp = json.loads(message_content.decode())
                print(temp)
                self.ipList = temp

    def sendMessage(self, data, sender):
        print("i am here")
        print(sender)
        print((self.ipList[0][1]))
        print(str(self.ipList[0][1]).encode())
        print(str(self.ipList[1][1]).encode())
        if sender == str(self.ipList[0][1]).encode():
            print("here")
            self.UDPserver.sendto(data, (self.ipList[1][0], self.ipList[1][1]))
        elif sender == str(self.ipList[1][1]).encode():
            print("here too")
            self.UDPserver.sendto(data, (self.ipList[0][0], self.ipList[0][1]))
        else:
            print("not working")


    def run_program(self):
        print(self.get_local_ip())
        while True:
            try:
                data, address = self.UDPserver.recvfrom(self.bufferSize)
                self.parse_message(data, address)
            except OSError:
                pass

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

def main():
    relay = Noise()
    relay.run_program()

if __name__ == "__main__":
    print(os.name)
    main()
