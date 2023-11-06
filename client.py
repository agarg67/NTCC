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
    
    def __init__(self, ipPass, portPass, portPass2):
        self.client_ip_address=ipPass
        self.clientCentralPort=portPass
        self.clientRelayPort=portPass2
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
        
        flagforServerConnection=True#will be made false
        
        while(flagforServerConnection==False):
            time.sleep(1)# will be changed 
        
        while(True):
            
            if(self.inputData!=""):
                print(self.inputData)
                localInputData=self.inputData
                self.inputData=""
                
                if(localInputData=="sendrelay"): # will be changed
                    print("hi")
                    message="dataSent"
                    
                    self.UDPClientRelaySocket.sendto(message.encode(),("10.155.162.199", 3953))#will be changed according to relay ip
                
            if(self.relayData!=""):
                print(self.relayData)
                localRelayData=self.relayData[0]
                localRelayAddr=self.relayData[1]
                self.relayData=""
                
                
                if(b"dataSent" in localRelayData): # will be changed
                    message="gotMessage"
                    self.UDPClientRelaySocket.sendto(message.encode(), localRelayAddr)
                
            if(self.centralData!=""):
                print(self.centralData)
                localCentralData=self.centralData
                self.relayData=""
            
            
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
    
    randPort2=random.randrange(1500, 50000, 1)
    
    while(randPort2==randPort):
        randPort2=random.randrange(1500, 50000, 1)
    
    print(randPort)
    print(randPort2)
    print(localIP)
    
    client = Client(localIP, randPort, randPort2)
    
    client.run_program()
    
    
    


main()