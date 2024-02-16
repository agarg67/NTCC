import sys
import os
import socket
import re
import pickle
import random
import threading
import time
import rsa

def find_available_port(start=49152, end=65535):
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                continue
    return None


# client class
# contains bulk of the code for socket communication
class Client:
    
    #variables initial state
    client_ip_address="localhost"
    clientCentralPort=0  
    clientRelayPort=0

    centralServerIp="localhost"
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
        
        
        #print(self.publicKeySelf)
        #print(self.privatekeySelf)
        
        qid_base=random.randrange(1001, 2000, 2)
        mid_base=random.randrange(2001, 3000, 3)
        
        self.questionId=random.randrange(qid_base, qid_base*10000, 4)
        self.messageId=random.randrange(mid_base, mid_base*10000, 3)
        self.createSocket()
    
    def is_port_available(self, port):
        """Check if a given port is available."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as temp_socket:
            try:
                temp_socket.bind(("", port))  # Try to bind to the given port
                temp_socket.listen(1)
            except OSError:
                return False  # Port is not available
            return True  # Port is available
    
    # used to create all sockets for communication and setup multi-threading
    def createSocket(self):
    
        self.clientCentralPort = find_available_port()
        print(self.clientCentralPort)
        
        if self.clientCentralPort is not None:
            self.UDPClientCentralSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            self.UDPClientCentralSocket.bind(("", self.clientCentralPort))

            self.threadCentral = threading.Thread(target=self.fetch_data_Central)
            self.threadCentral.daemon = True
            self.threadCentral.start()
            
        else:
            print("Failed to find an available central port.")

        self.clientRelayPort = find_available_port(start=self.clientCentralPort + 1)
        print(self.clientRelayPort)
        
        if self.clientRelayPort is not None:
            self.UDPClientRelaySocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            self.UDPClientRelaySocket.bind(("", self.clientRelayPort))

            self.threadRelay = threading.Thread(target=self.fetch_data_relay)
            self.threadRelay.daemon = True
            self.threadRelay.start()
        
        else:
            print("Failed to find an available relay port.")


    def closeSockets(self):
        """Closes the central and relay UDP sockets if they are open."""
        if self.UDPClientCentralSocket:
            try:
                self.UDPClientCentralSocket.close()
                print("Central socket closed successfully.")
            except Exception as e:
                print(f"Failed to close central socket: {e}")
            finally:
                self.UDPClientCentralSocket = None

        if self.UDPClientRelaySocket:
            try:
                self.UDPClientRelaySocket.close()
                print("Relay socket closed successfully.")
            except Exception as e:
                print(f"Failed to close relay socket: {e}")
            finally:
                self.UDPClientRelaySocket = None
            
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
        print("message to parse:\n", messageToParse)
        if("<" not in messageToParse):
            finalArr.append(messageToParse)
            return finalArr
        
        tempArr=messageToParse.split("<")
        print(tempArr)
        for i in range(len(tempArr)):
            tempArr[i]=tempArr[i].strip()
        
        print(tempArr) 
        for i in range(1,len(tempArr)):
            tempArr[i]=tempArr[i][0:len(tempArr[i])-1]
        
        print(tempArr)
        
        finalArr=tempArr
        
        return finalArr
        
            
    def sendPublickeyIP(self):
        try:
            messagPubkey= self.publicKeySelf.export_key(format='PEM').decode('utf-8')
            message=b"sendpubip" + b" <" + messagPubkey + b">" + b" <" + (str(self.client_ip_address)).encode() + b">"
            
            print(message)
            self.UDPClientCentralSocket.sendto(message,(self.centralServerIp, self.centralServerPort))
            #for testing
            #self.UDPClientCentralSocket.sendto(message.encode(),(self.forwarderServerIp, self.forwarderServerPort))
        except AttributeError as e:
            print(f"Failed to export public key: {e}")
        
    def sendQuestionToServer(self, question, answer):
        message="sendquestion" + " <" + str(self.questionId) + ">" + " <" + str(question) + ">" + " <" + str(answer) + ">"
        
        print(message.encode())
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
                    
                elif(localInputData=="sendquestion"):
                    print("send question:")
                    while(self.inputData==""):
                        time.sleep(0.0001)
                    
                    question=self.inputData
                    self.inputData=""
                    
                    print("Please enter your answer:")
                    
                    while(self.inputData==""):
                        time.sleep(0.0001)
                        
                    answer=self.inputData
                    self.inputData=""
                    
                    self.sendQuestionToServer(question, answer)
                        
                        
                    
                    
                
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
                
                if(b"ackcon" in localCentralData):
                    print("public key sent to server")
                    parsedDataArr=self.parseIncomingMessage(localCentralData.decode())
                    print(parsedDataArr)
                    
                    self.publickeyserver=parsedDataArr[1]
                    
                    self.publickeyserver=rsa.PublicKey.load_pkcs1(self.publickeyserver)
                    print(self.publickeyserver)
                    
                
                if(b"sendquestion" in localCentralData):
                    
                    questionAnswer=""
                    parsedMessage= self.parseIncomingMessage(localCentralData.decode())
                    print(parsedMessage[2])
                    
                    while(self.inputData==""):
                        time.sleep(0.0001)
                    
                    questionAnswer=self.inputData
                    self.inputData=""
                    
                    self.answerQuestion(parsedMessage[1], questionAnswer)
                    
                if(b"answerquestion" in localCentralData):
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
                    
                if(b"ackanswer" in localCentralData):
                    print("Your Answer has been accepted, we will move forward with completing the connection!")
                    
                    #space here to code for getting ip map and public key
                
                if(b"nakanswer" in localCentralData):
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
