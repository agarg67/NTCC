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

    centralServerIp="10.182.149.63"
    centralServerPort=20001 # port is fixed up

    forwarderServerIp="localhost"
    forwarderServerPort= 9999
    
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
    
    publickeyserver=""
    questionId=0
    messageId=0
    
    
    # init used to initialize the object
    def __init__(self, ipPass, portPass, portPass2): #self key word is needed as the first parameter in any function that belongs to the class and act opposite to this
        self.client_ip_address=ipPass
        self.clientCentralPort=portPass
        self.clientRelayPort=portPass2
        
        #key=rsa.generate(1024)
        self.publicKeySelf, self.privatekeySelf = rsa.newkeys(1024)
        #random_generator = Random.new().read
        #self.privatekeySelf=RSA.generate(1024, random_generator)
        #self.publicKeySelf=self.privatekeySelf.publickey()
        
        
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
        
    def terminal_printer(self, *dataToPrint):
        print(dataToPrint)
        
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
        self.terminal_printer("message to parse:\n", messageToParse)
        if(b"<" not in messageToParse):
            finalArr.append(messageToParse)
            return finalArr
        
        tempArr=messageToParse.split(b" <")
        self.terminal_printer(tempArr)
        
        if(b"ackcon" in tempArr[0]):
            tempArr[0]=tempArr[0].decode().strip()
            
            tempVar=b""
            for i in range(1,len(tempArr)):
                tempVar+=tempArr[i]
            tempArr[1]=tempVar
            print(tempArr[1][0:len(tempArr[1])-1])
            tempArr[1]= (tempArr[1][0:len(tempArr[1])-1]).decode()
                #pickle.loads(tempArr[1][0:len(tempArr[1])-1]))
            tempArr=tempArr[:2]
            print(tempArr)
        
        elif(b"sendcomreq" in tempArr[0]):
            tempArr[0]=tempArr[0].decode().strip()
            cmd=tempArr[0]
            
            tempVar=b""
            breakIndex=-1
            for i in range(1,len(tempArr)):
                if(b"ip_port" in tempArr[i]):
                    breakIndex=i
                    break
                tempVar+=tempArr[i]
                
            ipPortlist=tempArr[breakIndex]
            ipPortlist=ipPortlist[7:len(ipPortlist)-1].decode().strip()
            tempVar=tempVar[1][0:len(tempVar[1])-1].decode()
            loadedKey=rsa.PublicKey.load_pkcs1(tempVar)
            tempArr=[cmd, loadedKey, ipPortlist]
            
            
            
        # for i in range(len(tempArr)):
        #     tempArr[i]=tempArr[i].strip()
        
        self.terminal_printer(tempArr) 
        # for i in range(1,len(tempArr)):
        #     tempArr[i]=tempArr[i][0:len(tempArr[i])-1]
        
        #print(tempArr)
        
        finalArr=tempArr
        
        return finalArr
        
            
    def sendPublickeyIP(self):
        #messagPubkey= pickle.dumps(self.publicKeySelf, protocol=pickle.HIGHEST_PROTOCOL)
        pem = self.publicKeySelf.save_pkcs1()
        message=b"sendpubip" + b" <" + pem + b">" + b" <" + (str(self.client_ip_address)).encode() + b">"
        
        self.terminal_printer(message)
        self.UDPClientCentralSocket.sendto(message,(self.centralServerIp, self.centralServerPort))
        #for testing
        #self.UDPClientCentralSocket.sendto(message.encode(),(self.forwarderServerIp, self.forwarderServerPort))
        
        
    def sendQuestionToServer(self, question, answer):
        message="sendquestion" + " <" + str(self.questionId) + ">" + " <" + str(question) + ">" + " <" + str(answer) + ">"
        
        self.terminal_printer(message.encode())
        encmessage=rsa.encrypt(message.encode(), self.publickeyserver)
        self.UDPClientCentralSocket.sendto(encmessage,(self.centralServerIp, self.centralServerPort))
        
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
                self.terminal_printer(self.inputData)
                localInputData=self.inputData
                self.inputData=""

                ### The following if statements are bare-bone to purely test communication between client and server, will
                ### need to be changed to further continue sending messages to the server to store the information.
                if(localInputData=="CMD#?reqcon"):
                    message="reqcon"
                    message_bytes = message.encode('ascii')
                    self.UDPClientCentralSocket.sendto(message_bytes,(self.centralServerIp, self.centralServerPort)) # will be changed according to central server ip


            elif(self.inputData!=""):
                self.terminal_printer(self.inputData)
                localInputData=self.inputData
                self.inputData=""
                
                if(localInputData=="sendpubip"):
                    self.sendPublickeyIP()
                if(localInputData=="disconnectServer"):
                    message="receivedis"
                    self.UDPClientCentralSocket(message.encode(), (self.centralServerIp, self.centralServerPort))
                    
                # elif(localInputData=="sendquestion"):
                #     print("send question:")
                #     while(self.inputData==""):
                #         time.sleep(0.0001)
                    
                #     question=self.inputData
                #     self.inputData=""
                    
                #     print("Please enter your answer:")
                    
                #     while(self.inputData==""):
                #         time.sleep(0.0001)
                        
                #     answer=self.inputData
                #     self.inputData=""
                    
                #     self.sendQuestionToServer(question, answer)
                        
                        
                    
                    
                
            if(self.relayData!=""):
                self.terminal_printer(self.relayData)
                localRelayData=self.relayData[0]
                localRelayAddr=self.relayData[1]
                self.relayData=""
                
                if(b"dataSent" in localRelayData): # will be changed
                    message="gotMessage"
                    self.UDPClientRelaySocket.sendto(message.encode(), localRelayAddr)
                
            if(self.centralData!=""):
                self.terminal_printer(self.centralData)
                localCentralData=self.centralData[0]
                localaddr=self.centralData[1]
                self.centralData=""
                
                if(b"ackcon" in localCentralData):
                    self.terminal_printer("public key sent to server")
                    parsedDataArr=self.parseIncomingMessage(localCentralData)
                    self.terminal_printer(parsedDataArr)
                    
                    self.publickeyserver=parsedDataArr[1]
                    
                    messagetoenc=b"hello"

                    self.publickeyserver = rsa.PublicKey.load_pkcs1(self.publickeyserver)

                    encmessage=rsa.encrypt(messagetoenc, self.publickeyserver)
                    self.terminal_printer("test encryption:")
                    self.terminal_printer(encmessage)
                    
                    
                    
                    self.terminal_printer("please enter your question:")
                    while(self.inputData==""):
                        time.sleep(0.0001)
                    
                    question=self.inputData
                    self.inputData=""
                    
                    self.terminal_printer("Please enter your answer:")
                    
                    while(self.inputData==""):
                        time.sleep(0.0001)
                        
                    answer=self.inputData
                    self.inputData=""
                    
                    self.sendQuestionToServer(question, answer)
                    
                    
                    
                
                if(b"sendquestion" in localCentralData):
                    
                    questionAnswer=""
                    parsedMessage= self.parseIncomingMessage(localCentralData.decode())
                    self.terminal_printer(parsedMessage[2])
                    
                    while(self.inputData==""):
                        time.sleep(0.0001)
                    
                    questionAnswer=self.inputData
                    self.inputData=""
                    
                    self.answerQuestion(parsedMessage[1], questionAnswer)
                    
                if(b"answerquestion" in localCentralData):
                    acceptOrReject="No"
                    
                    parsedMessage = self.parseIncomingMessage(localCentralData)
                    
                    self.terminal_printer("Recieved the following answer:")
                    self.terminal_printer(parsedMessage[2])
                    self.terminal_printer("reply yes to accept, reply with anything else to reject")
                    
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
                    
                if(b"ackanswer" in localCentralData):
                    self.terminal_printer("Your Answer has been accepted, we will move forward with completing the connection!")
                    
                    #space here to code for getting ip map and public key
                
                if(b"nakanswer" in localCentralData):
                    self.terminal_printer("Your answer has been rejected, please try from begining. Current session is terminated")
                    
                    #space here to code for more things
                    
                if(b"sendcomreq" in localCentralData):
                    print("got list of ip address+port")
                    parsedMessage=self.parseIncomingMessage(localCentralData)
                    self.publickeyPeer=parsedMessage[1]
                    ipportListstring=parsedMessage[2]
                    
                    
                localCentralData=""
                    
                          

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

def main(): # entry function of the program
    
    #fetching the ip address here
    localIP=get_local_ip() 
    
    #setting ports for socket communication
    randPort=random.randrange(1500, 50000, 1)
    
    randPort2=random.randrange(1500, 50000, 1)
    
    while(randPort2==randPort or (randPort==20001 or randPort2==20001)):
        randPort2=random.randrange(1500, 50000, 1)
    
    print("central port:",randPort)
    print("relay port:",randPort2)
    print(localIP)
    
    #creating a client object to start program 
    client = Client(localIP, randPort, randPort2)
    
    # we enter client program, everything beyond this point is coded inside the client class
    client.run_program()

main() # starting the program