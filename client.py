import sys
import os
import socket
import re
import pickle
import random
import threading
import time

class Client:
    
    client_ip_address="0.0.0.0"
    clientCentralPort=0
    clientRelayPort=0
    
    
    
    centralServerIp="0.0.0.0"
    centralServerPort=0
    
    relayServerIpList=[]
    relayServerPortList=[]
    
    relayServerIpporttupleList=[]
    
    inputData=""
    
    centralData=""
    
    relayData=""
    
    bufferSize=4096
    
    def __init__(self, ipPass, portPass):
        self.client_ip_address=ipPass
        self.clientCentralPort=portPass
        self.createSocket()
    
    def createSocket(self):
        
        self.threadInput=threading.Thread(target=self.asynchrounous_input)
        self.threadInput.daemon=True
        self.threadInput.start()
        
        self.UDPClientCentralSocket=socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
        self.UDPClientCentralSocket.bind(("", self.clientCentralPort))
        
        
        self.threadCentral=threading.Thread(target=self.fetch_data_Central)
        self.threadCentral.daemon=True
        self.threadCentral.start()
        
        self.UDPClientRelaySocket=socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
        self.UDPClientRelaySocket.bind(("", self.clientRelayPort))
        
        self.threadRelay=threading.Thread(target=self.fetch_data_relay)
        self.threadRelay.daemon=True
        self.threadRelay.start()
        
        
    def asynchrounous_input(self):
        
        while(True):
            inp=input()
            self.inputData=inp
            
    def fetch_data_Central(self):
        while(True):
            inp=self.UDPClientCentralSocket.recvfrom(self.bufferSize)
            self.centralData=inp
            
    def fetch_data_relay(self):
        while(True):
            inp=self.UDPClientRelaySocket.recvfrom(self.bufferSize)
            self.relayData=inp
            
    def run_program(self):
        
        while(True):
            
            if(self.inputData!=""):
                print(self.inputData)
                self.inputData=""
            
            
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('192.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP    

def main():
    
    localIP=get_local_ip() 
    randPort=random.randrange(1500, 50000, 1)
    
    print(randPort)
    print(localIP)
    
    client = Client(localIP, randPort)
    
    client.run_program()
    
    
    


main()