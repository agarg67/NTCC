import sys
import os
import socket
import re
import pickle
import random
import threading
import time
import rsa

# client class
# contains bulk of the code for socket communication
class Client:
    
    #variables initial state
    client_ip_address="localhost"
    clientCentralPort=0  
    clientRelayPort=0

    centralServerIp="192.168.244.140"
    centralServerPort=20001 # port is fixed up
    
    relayServerIpList=[]
    relayServerPortList=[]
    
    relayServerIpporttupleList=[]
    
    inputData=""
    
    centralData=""
    
    relayData=""
    
    # this is the fixed buffersixe for recieving data
    bufferSize=4096
    
    publicKeySelf=""
    privatekeySelf=""
    
    publickeyPeer=""
    
    questionId=0
    messageId=0
    
    
    # init used to initialize the object
    def __init__(self, ipPass, portPass, portPass2): #self key word is needed as the first parameter in any function that belongs to the class and act opposite to this
        self.client_ip_address=ipPass
        self.clientCentralPort=portPass
        self.clientRelayPort=portPass2
        
        self.publicKeySelf, self.privatekeySelf = rsa.newkeys(2048)
        
        print(self.publicKeySelf)
        print(self.privatekeySelf)
        
        qid_base=random.randrange(1001, 2000, 2)
        mid_base=random.randrange(2001, 3000, 3)
        
        self.questionId=random.randrange(qid_base, qid_base*10000, 4)
        self.messageId=random.randrange(mid_base, mid_base*10000, 3)
        self.createSocket()
    
    # used to create all sockets for communication and setup multi-threading
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
            
    def parseIncomingMessage(self, messageToParse):
        finalArr=[]
        
        if("<" not in messageToParse):
            finalArr.append(messageToParse)
            return finalArr
        
        tempArr=messageToParse.split("<")
        
        for i in range(len(tempArr)):
            tempArr[i]=tempArr[i].strip()
            
        for i in range(1,len(tempArr)):
            tempArr[i]=tempArr[i][1:len(tempArr)-1]
        
        finalArr=tempArr
        
        return finalArr
        
            
    def sendPublickeyIP(self):
        message="sendpubip" + " <" + str(self.publicKeySelf) + ">" + " <" + str(self.client_ip_address) + ">"
        
        print(message)
        self.UDPClientCentralSocket.sendto(message.encode(),(self.centralServerIp, self.centralServerPort))
        
        
    def sendQuestionToServer(self, question):
        message="sendquestion" + " <" + str(self.questionId) + ">" + " <" + str(question) + ">"
        
        self.UDPClientCentralSocket.sendto(message.encode(),(self.centralServerIp, self.centralServerPort))
        
        self.questionId+=1
        
    def sendMessage(self, message):
        message="message" + " <" + str(self.messageId) + ">" + " <" + message + ">"
        
        self.messageId+=1
    
    def answerQuestion(self, qid, answer):
        message="answerquestion" + " <" + str(qid) + ">" + " <" + answer + ">"
        
        self.UDPClientCentralSocket.sendto(message.encode(),(self.centralServerIp, self.centralServerPort))
        
    
    def run_program(self): # the whole communication of the program happens through here and so has a while true loop to prevent exit
        
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
                if(localInputData=="CMD#?reqcon"):
                    message="reqcon"
                    message_bytes = message.encode('ascii')
                    self.UDPClientCentralSocket.sendto(message_bytes,(self.centralServerIp, self.centralServerPort)) # will be changed according to central server ip


            elif(self.inputData!=""):
                print(self.inputData)
                localInputData=self.inputData
                self.inputData=""
                
                if(localInputData=="sendpubip"):
                    self.sendPublickeyIP()
                    
                
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
                localaddr=self.centralData[1]
                self.centralData=""
                
                if(localCentralData=="ackpubip"):
                    print("public key sent to server")
                
                if("sendquestion" in localCentralData):
                    
                    questionAnswer=""
                    parsedMessage= self.parseIncomingMessage(localCentralData.decode())
                    print(parsedMessage[2])
                    
                    while(self.inputData==""):
                        time.sleep(0.0001)
                    
                    questionAnswer=self.inputData
                    self.inputData=""
                    
                    self.answerQuestion(parsedMessage[1], questionAnswer)
                    
                if("answerquestion" in localCentralData):
                    acceptOrReject="No"
                    
                    parsedMessage = self.parseIncomingMessage(localCentralData.decode())
                    
                    print("Recieved the following answer:")
                    print(parsedMessage[2])
                    print("reply yes to accept, reply with anything else to reject")
                    
                    questionAnswer=""
                    while(self.inputData==""):
                        time.sleep(0.0001)
                    
                    questionAnswer=self.inputData
                    self.inputData=""
                    
                    replytoSend=""
                    
                    if("yes" in questionAnswer.lower()):
                        replytoSend="ackanswer" + " <" + str(parsedMessage[1]) + ">"
                    else:
                        replytoSend="nakanswer" + " <" + str(parsedMessage[1]) + ">"
                    
                    self.UDPClientCentralSocket.sendto(replytoSend.encode(),(self.centralServerIp, self.centralServerPort))
                    
                if("ackanswer" in localCentralData):
                    print("Your Answer has been accepted, we will move forward with completing the connection!")
                    
                    #space here to code for getting ip map and public key
                
                if("nakanswer" in localCentralData):
                    print("Your answer has been rejected, please try from begining. Current session is terminated")
                    
                    #space here to code for more things
                    
                          

def get_local_ip(): # this method is used to resolve your own ip address
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

def main(): # entry function of the program
    
    #fetching the ip address here
    localIP=get_local_ip() 
    
    #setting ports for socket communication
    randPort=random.randrange(1500, 50000, 1)
    
    randPort2=random.randrange(1500, 50000, 1)
    
    while(randPort2==randPort):
        randPort2=random.randrange(1500, 50000, 1)
    
    print("central port:",randPort)
    print("relay port:",randPort2)
    print(localIP)
    
    #creating a client object to start program 
    client = Client(localIP, randPort, randPort2)
    
    # we enter client program, everything beyond this point is coded inside the client class
    client.run_program()

main() # starting the program