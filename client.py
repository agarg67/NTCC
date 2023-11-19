import sys
import os
import socket
import re
import pickle
import random
import threading
import time
import rsa

class Client:
    
    client_ip_address="0.0.0.0"
    clientCentralPort=0
    clientRelayPort=0

    centralServerIp="127.0.0.1"
    centralServerPort=20001
    
    relayServerIpList=[]
    relayServerPortList=[]
    
    relayServerIpporttupleList=[]
    
    inputData=""
    
    centralData=""
    
    relayData=""
    
    bufferSize=4096
    
    publicKeySelf=""
    privatekeySelf=""
    
    publickeyPeer=""
    
    questionId=0
    messageId=0
    
    
    def __init__(self, ipPass, portPass, portPass2):
        self.client_ip_address=ipPass
        self.clientCentralPort=portPass
        self.clientRelayPort=portPass2
        qid_base=random.randrange(1001, 2000, 2)
        mid_base=random.randrange(2001, 3000, 3)
        
        self.questionId=random.randrange(qid_base, qid_base*10000, 4)
        self.messageId=random.randrange(mid_base, mid_base*10000, 3)
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
            
    def sendPublickey(self):
        message="sendpubip"
        
    def sendQuestionToServer(self, question):
        message="sendquestion" + "<" + str(self.questionId) + ">" + "<" + str(question) + ">"
        
        
        self.questionId+=1
        
    def sendMessage(self, message):
        message="message"
        
        self.messageId+=1
        
    ### Will need to separate the function into 2 different functions, one for the central server and one for communication between the forwarder ##
    def run_program(self):
        
        flagforServerConnection=True#will be made false
        
        while(flagforServerConnection==False):
            time.sleep(1)# will be changed 
        
        while(True):
            
            if(self.inputData!="" and "CMD#?" in self.inputData):
                print(self.inputData)
                localInputData=self.inputData
                self.inputData=""

                ### The following if statements are bare-bone to purely test communication between client and server, will
                ### need to be changed to further continue sending messages to the server to store the information.
                if(localInputData=="reqcon"):
                    message="ackcon"
                    message_bytes = message.encode('ascii')
                    self.UDPClientCentralSocket.sendto(message_bytes,(self.centralServerIp, self.centralServerPort)) # will be changed according to central server ip

                if (localInputData == "initiate"):
                    message = "comrequest"
                    message_bytes = message.encode('ascii')
                    self.UDPClientCentralSocket.sendto(message_bytes, (self.centralServerIp, self.centralServerPort))

                if(localInputData=="Public Key"):
                    message="ackpubip"
                    message_bytes = message.encode('ascii')
                    self.UDPClientCentralSocket.sendto(message_bytes,(self.centralServerIp, self.centralServerPort))

                if(localInputData=="question"):
                    message="ackquestion"
                    message_bytes = message.encode('ascii')
                    self.UDPClientCentralSocket.sendto(message_bytes,(self.centralServerIp, self.centralServerPort))

                if(localInputData=="answer"):
                    message="ackanswer"
                    message_bytes = message.encode('ascii')
                    self.UDPClientCentralSocket.sendto(message_bytes,(self.centralServerIp, self.centralServerPort))

                if(localInputData=="disconnect"):
                    message="ackdis"
                    message_bytes = message.encode('ascii')
                    self.UDPClientCentralSocket.sendto(message_bytes,(self.centralServerIp, self.centralServerPort))

                ## Tests for unknown input into the central server ##
                if (localInputData == ""):
                    message = localInputData
                    message_bytes = message.encode('ascii')
                    self.UDPClientCentralSocket.sendto(message_bytes, (self.centralServerIp, self.centralServerPort))
                    
            elif(self.inputData!=""):
                localInputData=self.inputData
                self.inputData=""
                
                self.sendQuestionToServer(localInputData)
            
                
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
                localCentralData=self.centralData[0]
                
                self.centralData=""

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