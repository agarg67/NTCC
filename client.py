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

    centralServerIp="10.155.131.118"
    centralServerPort=20001 # port is fixed up

    forwarderServerIp="localhost"
    forwarderServerPort= 9999
    
    relayServerIpList=[]
    relayServerPortList=[]
    
    relayServerIpporttupleList=[[]]
    
    inputData=""
    
    
    centralData=""
    
    relayData=""
    
    # this is the fixed buffersixe for recieving data
    bufferSize=128000
    
    publicKeySelf=""
    privatekeySelf=""
    
    publickeyPeer=""
    
    publickeyserver=""
    questionId=0
    messageId=0
    
    communicationFlag=False
    
    # init used to initialize the object
    def __init__(self, ipPass, portPass, portPass2): #self key word is needed as the first parameter in any function that belongs to the class and act opposite to this
        self.client_ip_address=ipPass
        self.clientCentralPort=portPass
        self.clientRelayPort=portPass2
        
        #key=rsa.generate(1024)
        self.publicKeySelf, self.privatekeySelf = rsa.newkeys(2048)
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
            
        elif(b"comrequest" in tempArr[0]):
            tempArr[0]=tempArr[0].decode().strip()
            cmd=tempArr[0]
            tempVar=tempArr[1][0:len(tempArr[1])-1]
            tempVar=tempVar.split(",")
            print(tempVar)
            
            tempArr=[cmd, tempVar]
            
            
            
        # for i in range(len(tempArr)):
        #     tempArr[i]=tempArr[i].strip()
        
        #self.terminal_printer(tempArr) 
        print(tempArr)
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
        #encmessage=rsa.encrypt(message.encode(), self.publickeyserver)
        encmessage=self.encrypt_data_central_server(message.encode())
        self.UDPClientCentralSocket.sendto(encmessage,(self.centralServerIp, self.centralServerPort))
        
        self.questionId+=1
        
    def sendMessage(self, message):
        message="message" + " <" + str(self.messageId) + ">" + " <" + message + ">"
        
        encmessage=self.encrypt_data_forwarder(message.encode())
        self.UDPClientRelaySocket.sendto(encmessage, (self.forwarderServerIp, self.forwarderServerPort))
        self.messageId+=1
    
    def answerQuestion(self, qid, answer):
        message="answerquestion" + " <" + str(qid) + ">" + " <" + answer + ">"
        encmessage=self.encrypt_data_central_server(message.encode())
        
        self.UDPClientCentralSocket.sendto(encmessage,(self.centralServerIp, self.centralServerPort))
        
    def decrypt_data(self, data_to_decrypt):
        decrypted_data=b""
        if len(data_to_decrypt)<=256:
            print("normal decrypted data")
            decrypted_data=rsa.decrypt(data_to_decrypt, self.privatekeySelf)
        else:
            for i in range(0, len(data_to_decrypt), 256):
                chunk=data_to_decrypt[i:i+256]
                chunk=rsa.decrypt(chunk, self.privatekeySelf)
                print("decrypted chunk:", chunk)
                decrypted_data+=chunk
            
        return decrypted_data
    
    def encrypt_data_central_server(self, data_to_encrypt):
        keyForEnc=self.publickeyserver
        encrypted_data=b""
        if len(data_to_encrypt)<=245:
            encrypted_data=rsa.encrypt(data_to_encrypt, keyForEnc)
        else:
            for i in range(0,len(data_to_encrypt), 245):
                encrypted_data+=rsa.encrypt(data_to_encrypt[i:i+245], keyForEnc)
        print("encrypted data:")
        print(encrypted_data)
           
        return encrypted_data
    
    def encrypt_data_forwarder(self, data_to_encrypt):
        keyForEnc=self.publickeyPeer
        encrypted_data=b""
        if len(data_to_encrypt)<=245:
            encrypted_data=rsa.encrypt(data_to_encrypt, keyForEnc)
        else:
            for i in range(0,len(data_to_encrypt), 245):
                encrypted_data+=rsa.encrypt(data_to_encrypt[i:i+245], keyForEnc)
        print("encrypted data:")
        print(encrypted_data)
           
        return encrypted_data
        
    def run_program(self): # the whole communication of the program happens through here and so has a while true loop to prevent exit
        
        flagforServerConnection=True#will be made false
        
        while(flagforServerConnection==False):
            time.sleep(0.00001)# will be changed 
        
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
                elif(localInputData=="disconnectServer"):
                    message="receivedis"
                    self.UDPClientCentralSocket.sendto(message.encode(), (self.centralServerIp, self.centralServerPort))
                    
                elif(localInputData=="sendquestion"):
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
                else:
                    
                    if(self.communicationFlag==True):
                        self.sendMessage(localInputData)
                
                localInputData=""
                    
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
                
                localRelayData=self.decrypt_data(localRelayData)
                print(localRelayData)
                
                if(b"dataSent" in localRelayData): # will be changed
                    message="gotMessage"
                    self.UDPClientRelaySocket.sendto(message.encode(), localRelayAddr)
                
            if(self.centralData!=""):
                self.terminal_printer(self.centralData)
                localCentralData=self.centralData[0]
                localaddr=self.centralData[1]
                self.centralData=""
                
                localCentralData=self.decrypt_data(localCentralData)
                print("decryptedData")
                print(localCentralData)
                
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
                    
                    
                if(b"unameCS" in localCentralData):
                    self.terminal_printer("What's your name?")
                    self.terminal_printer("Enter first 3 letters of your last name and first 1 letters of your last name")
                    name=""
                    nameFlag=False
                    while(nameFlag==False):
                        while(self.inputData==""):
                            time.sleep(0.0001)
                        name=self.inputData
                        self.inputData=""
                        
                        name=name.strip()
                        
                        if(len(name)>4):
                            print("incorrect format")
                        else:
                            nameFlag=True
                    
                    name=name[0:3] + "##" + name[3:]
                    message= "sendnameserver " + "<" + name +">"
                    enc=self.encrypt_data_central_server(message.encode())
                    
                    self.UDPClientCentralSocket.sendto(enc, (self.centralServerIp, self.centralServerPort))
                    
                if(b"comrequest" in localCentralData):
                    self.terminal_printer("please choose the partner to communicate with (note please put name exactly as you see it)")
                    partnerName=""
                    parsedMessage=self.parseIncomingMessage(localCentralData)
                    
                    nameArray=parsedMessage[1]
                    
                    for i in nameArray:
                        print(i)
                        
                    while(self.inputData==""):
                        time.sleep(0.0001)
                    
                    partnerName=self.inputData
                    self.inputData=""
                    
                    partnerName=partnerName.strip()
                    print(partnerName)
                    
                    while(partnerName not in nameArray):
                        print("name not present, please choose again")
                        while(self.inputData==""):
                            time.sleep(0.0001)
                    
                        partnerName=self.inputData
                        self.inputData=""
                    
                        partnerName=partnerName.strip()
                        print(partnerName)
                        
                    message= "sendpartnerserver " + "<" + partnerName +">"
                    enc=self.encrypt_data_central_server(message.encode())
                    
                    self.UDPClientCentralSocket.sendto(enc, (self.centralServerIp, self.centralServerPort))
                    
                    
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
                    
                    
                    #may be moved
                    self.communicationFlag=True
                    print("now please use your textbox to send messages to your partner")
                    
                
                if(b"nakanswer" in localCentralData):
                    self.terminal_printer("Your answer has been rejected, please try from begining. Current session is terminated")
                    
                    #space here to code for more things
                    
                if(b"sendcomreq" in localCentralData):
                    print("got ip address+port")
                    parsedMessage=self.parseIncomingMessage(localCentralData)
                    self.publickeyPeer=parsedMessage[1]
                    ipportListstring=parsedMessage[2]
                    ipportListstringsplit=ipportListstring.strip()
                    
                    tempVarArr=[]
                    #for i in range(len(ipportListstringsplit)):
                        #tempVar=ipportListstringsplit.at(i)
                    tempVar=ipportListstringsplit
                    tempVar=tempVar.split(",")
                    tempVar[0]=tempVar.strip()
                    tempVar[1]=int(tempVar[1])
                    tempVarArr.append(tempVar)
                    
                    self.forwarderServerIp=tempVar[0]
                    self.forwarderServerPort=tempVar[1]
                    
                    self.relayServerIpporttupleList=tempVarArr
                    
                    for j in self.relayServerIpporttupleList:
                        self.relayServerIpList.append(j[0])
                        self.relayServerPortList.append(j[1])
                    
                    print("stored ip-port")
                        
                    
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