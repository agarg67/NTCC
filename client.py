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
from mainGUI import ClientGUI
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QThread, pyqtSignal

# client class
# contains bulk of the code for socket communication
class Client:
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
    
    #variables initial state
    client_ip_address="localhost"
    clientCentralPort=0  
    clientRelayPort=0


    centralServerIp="192.168.212.140"
    centralServerPort=20001 # port is fixed up

    forwarderServerIp="192.168.191.165"
    forwarderServerPort= 9999
    
    relayServerIpList=[]
    relayServerPortList=[]
    
    relayServerIpporttupleList=[[]]
    
    inputData=""
    
    app = QApplication(sys.argv)
    gui = ClientGUI()
    
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
        
        self.gui.show()
        
        #self.gui.messageLog.append("central port:" + str(portPass))
        #self.gui.messageLog.append("relay port:" + str(portPass2))
        #self.gui.messageLog.append(str(ipPass))
        #self.gui.messageLog.append(str(self.publicKeySelf))
        #self.gui.messageLog.append(str(self.privatekeySelf))


        #print(self.publicKeySelf)
        #print(self.privatekeySelf)
        
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
        
        self.threadRUN=threading.Thread(target=self.run_program)
        self.threadRUN.daemon=True
        self.threadRUN.start()
        
        self.threadGUI=threading.Thread(target=self.app.exec_())
        self.threadGUI.daemon=True
        self.threadGUI.start()
        
        
        
    def terminal_printer(self, *dataToPrint):
        #print(dataToPrint)
        
        for i in dataToPrint:
            self.gui.messageLog.append(str(i))
        
    def asynchrounous_input(self):
        self.gui.currentCommand=""
        while(True):
            if(self.gui.currentCommand!=""):
                self.inputData = self.gui.getCommand()
                self.gui.currentCommand=""
            
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
        #self.terminal_printer("message to parse:\n", messageToParse)
        if(b"<" not in messageToParse):
            finalArr.append(messageToParse)
            return finalArr
        
        tempArr=messageToParse.split(b" <")
        print(tempArr)
        
        if(b"ackcon" in tempArr[0]):
            tempArr[0]=tempArr[0].decode().strip()
            
            tempVar=b""
            for i in range(1,len(tempArr)):
                tempVar+=tempArr[i]
            tempArr[1]=tempVar
            #print(tempArr[1][0:len(tempArr[1])-1])
            tempArr[1]= (tempArr[1][0:len(tempArr[1])-1]).decode()
                #pickle.loads(tempArr[1][0:len(tempArr[1])-1]))
            tempArr=tempArr[:2]
            #print(tempArr)
        
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
            
            print("supposed key:",tempVar)
            ipPortlist=tempArr[breakIndex]
            ipPortlist=ipPortlist[7:len(ipPortlist)-1].decode().strip()
            tempVar=tempVar[0:len(tempVar)-1].decode()
            loadedKey=rsa.PublicKey.load_pkcs1(tempVar)
            tempArr=[cmd, loadedKey, ipPortlist]
            
        elif(b"comrequest" in tempArr[0]):
            tempArr[0]=tempArr[0].decode().strip()
            cmd=tempArr[0]
            tempVar=tempArr[1][0:len(tempArr[1])-1]
            #print(tempVar)
            if(b"NO OTHER" not in tempVar):
                #print(tempVar)
                tempVar=json.loads(tempVar.decode())
            else:
                tempVar=tempVar.decode().strip()
            
            #print(tempVar)
            # for i in range(len(tempVar)):
            #     tempVar[i]=tempVar[i][2:len(tempVar[1])-1]
            
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
        
        print(message)
        self.UDPClientCentralSocket.sendto(message,(self.centralServerIp, self.centralServerPort))
        #for testing
        #self.UDPClientCentralSocket.sendto(message.encode(),(self.forwarderServerIp, self.forwarderServerPort))
        
        
    def sendQuestionToServer(self, question, answer):
        message="sendquestion" + " <" + str(self.questionId) + ">" + " <" + (str(self.client_ip_address)) + ">" + " <" + str(question) + ">" + " <" + str(answer) + ">" + " <" + str(self.clientRelayPort) + ">"
        
        print(message.encode())
        #encmessage=rsa.encrypt(message.encode(), self.publickeyserver)
        encmessage=self.encrypt_data_central_server(message.encode())
        self.UDPClientCentralSocket.sendto(encmessage,(self.centralServerIp, self.centralServerPort))
        
        self.questionId+=1
        
    def sendMessage(self, message):
        
        message_content="message" + " <" + str(self.messageId) + ">" + " <" + message +">"
        
        encmessage=self.encrypt_data_forwarder(message_content.encode())
        
        

        message=b"sendmessage"+ b" <" + encmessage + b">"  + b" <" + str(self.forwarderServerIp).encode() +  b">" 
        
        message=message
        #encmessage=self.encrypt_data_forwarder(message.encode())
        
        print("message bieng sent")
        print(message)
        self.UDPClientRelaySocket.sendto(message, (self.forwarderServerIp, self.forwarderServerPort))
        self.messageId+=1
    
    def answerQuestion(self, qid, answer):
        message="answerquestion"+ " <" + answer + ">" + " <" + str(self.client_ip_address) +">"
        encmessage=self.encrypt_data_central_server(message.encode())

        self.UDPClientCentralSocket.sendto(encmessage,(self.centralServerIp, self.centralServerPort))

    def decrypt_data(self, data_to_decrypt):
        print("data to decrypt:")
        print(data_to_decrypt)
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
        #keyForEnc=self.publicKeySelf
        encrypted_data=b""
        if len(data_to_encrypt)<=245:
            encrypted_data=rsa.encrypt(data_to_encrypt, keyForEnc)
        else:
            for i in range(0,len(data_to_encrypt), 245):
                encrypted_data+=rsa.encrypt(data_to_encrypt[i:i+245], keyForEnc)
        print("encrypted data:")
        print(encrypted_data)

        return encrypted_data
    def clear_input_data(self):
        self.inputData=""
        self.gui.currentCommand=""
        
    def run_program(self): # the whole communication of the program happens through here and so has a while true loop to prevent exit

        self.flagforServerConnection=False
        self.flagForackcon=False
        self.communicationFlag=False
        
        self.terminal_printer("Please press sendpubip button to start the process")
        while(True):
            
            # if(self.inputData!="" and "CMD#?" in self.inputData):
            #     self.terminal_printer(self.inputData)
            #     localInputData=self.inputData
            #     self.inputData=""

            #     ### The following if statements are bare-bone to purely test communication between client and server, will
            #     ### need to be changed to further continue sending messages to the server to store the information.
            #     if(localInputData=="CMD#?reqcon"):
            #         message="reqcon"
            #         message_bytes = message.encode('ascii')
            #         self.UDPClientCentralSocket.sendto(message_bytes,(self.centralServerIp, self.centralServerPort)) # will be changed according to central server ip


            if(self.inputData!=""):
                
                self.terminal_printer(self.inputData)
                localInputData=self.inputData
                self.gui.currentCommand=""
                self.clear_input_data()

                if(localInputData=="sendpubip" or localInputData=="CMD#?sendpubip"):
                    self.sendPublickeyIP()
                elif(localInputData=="CMD#?disconnectServer"):
                    
                    message="receivedis"
                    # encmessage=self.encrypt_data_forwarder(message.encode())
                    # self.UDPClientCentralSocket.sendto(message.encode(), (self.centralServerIp, self.centralServerPort))
                    self.sendMessage(message)
                    self.terminal_printer("Thanks a lot, we are disconnecting you.\n Please restart the process to initate communication with another user.")
                    self.communicationFlag=False
                    self.flagforServerConnection=False
                    self.flagForackcon=False
                    

                elif(localInputData=="sendquestion" or localInputData=="CMD#?sendquestion"):

                    if(self.flagForackcon==True):
                        self.terminal_printer("please enter your question:")
                        while(self.inputData==""):
                            time.sleep(0.0001)

                        question=self.inputData
                        self.terminal_printer(question)
                        self.clear_input_data()

                        self.terminal_printer("Please enter your answer:")

                        while(self.inputData==""):
                            time.sleep(0.0001)

                        answer=self.inputData
                        self.terminal_printer(answer)
                        self.clear_input_data()

                        self.sendQuestionToServer(question, answer)
                    else:
                        self.terminal_printer("ERRROR: pub key not accepted yet")

                elif(localInputData=="comrequest" or localInputData=="CMD#?comrequest"):
                    if(self.flagforServerConnection==True):

                        key_phrase="client_server"
                        message= "comrequest" + " <" + key_phrase + ">" + " <" + ((str(self.client_ip_address))) + ">"

                        encmessage=self.encrypt_data_central_server(message.encode())

                        self.UDPClientCentralSocket.sendto(encmessage, (self.centralServerIp, self.centralServerPort))

                    else:
                        self.terminal_printer("can't start iniate process question not accepted yet")

                else:

                    if(self.communicationFlag==True):
                        self.sendMessage(localInputData)
                    else:
                        self.terminal_printer("The peer has not connected yet, please first finish the process")


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
                print("relay data")
                
                localRelayData=self.relayData[0]
                localRelayAddr=self.relayData[1]
                self.relayData=""
                
                #self.terminal_printer(localRelayData)
                localRelayData=self.decrypt_data(localRelayData)
                print(localRelayData)
                
                if(b"receivedis" in localRelayData):
                    self.terminal_printer("The peer has disconnected please start the process again to connect to a diffrent peer.")
                    self.communicationFlag=False
                    self.flagforServerConnection=False
                    self.flagForackcon=False
                    

                elif(b"message" in localRelayData): # will be changed
                    parsedData=self.parseIncomingMessage(localRelayData)
                    
                    messagetodisplay=parsedData[2][:len(parsedData[2])-1].decode()
                    self.terminal_printer(messagetodisplay)
                

                localRelayData=""

            if(self.centralData!=""):
                #self.terminal_printer(self.centralData)
                localCentralData=self.centralData[0]
                localaddr=self.centralData[1]
                self.centralData=""

                localCentralData=self.decrypt_data(localCentralData)
                print("decryptedData")
                print(localCentralData)

                if(b"ackcon" in localCentralData):
                    self.terminal_printer("public key sent to server")
                    parsedDataArr=self.parseIncomingMessage(localCentralData)
                    #self.terminal_printer(parsedDataArr)

                    self.publickeyserver=parsedDataArr[1]

                    messagetoenc=b"hello"

                    self.publickeyserver = rsa.PublicKey.load_pkcs1(self.publickeyserver)

                    encmessage=rsa.encrypt(messagetoenc, self.publickeyserver)
                    #self.terminal_printer("test encryption:")
                    #self.terminal_printer(encmessage)
                    self.flagForackcon=True

                elif(b"ackquestion" in localCentralData):
                    self.terminal_printer("your question has been accepted")
                    self.terminal_printer("Please press comrequest button when ready")
                    self.flagforServerConnection=True

                if(b"unameCS" in localCentralData):
                    self.terminal_printer("What's your name?")
                    self.terminal_printer("Enter first 2 letters of your first name and first 2 letters of your last name")
                    name=""
                    nameFlag=False
                    while(nameFlag==False):
                        while(self.inputData==""):
                            time.sleep(0.0001)
                        name=self.inputData
                        self.terminal_printer(name)
                        #self.inputData=""
                        self.clear_input_data()

                        name=name.strip()

                        if(len(name)!=4):
                            self.terminal_printer("Incorrect format, please try again")
                        else:
                            nameFlag=True
                            
                    strTochooseFrom="!@#$*"
                    
                    randChar1=random.choice(strTochooseFrom)
                    randChar2=random.choice(strTochooseFrom)
                    randStr=randChar2+randChar1
                    
                    name=name[0:3] + randStr + name[3:]
                    
                    message= "sendnameserver " + "<" + name +">" + " <" + (str(self.client_ip_address)) + ">"
                    enc=self.encrypt_data_central_server(message.encode())

                    self.UDPClientCentralSocket.sendto(enc, (self.centralServerIp, self.centralServerPort))
                    self.terminal_printer("your name has been accepted, and sent to the server")
                    self.terminal_printer("Please press the sendquestion button when you are ready")

                if(b"comrequest" in localCentralData):
                    self.terminal_printer("please choose the partner to communicate with (note please put name exactly as you see it)")
                    partnerName=""
                    parsedMessage=self.parseIncomingMessage(localCentralData)

                    if("NO OTHER" not in parsedMessage[1]):
                        nameArray=parsedMessage[1]

                        for i in nameArray:
                            self.terminal_printer(i)

                        while(self.inputData==""):
                            time.sleep(0.0001)

                        partnerName=self.inputData
                        self.clear_input_data()

                        partnerName=partnerName.strip()
                        print(partnerName)

                        while(partnerName not in nameArray):
                            print("name not present, please choose again")
                            while(self.inputData==""):
                                time.sleep(0.0001)

                            partnerName=self.inputData
                            self.clear_input_data()

                            partnerName=partnerName.strip()
                            print(partnerName)

                        message= "sendpartnerserver " + "<" + partnerName +">" + " <" + (str(self.client_ip_address))+">" 
                        enc=self.encrypt_data_central_server(message.encode())

                        self.UDPClientCentralSocket.sendto(enc, (self.centralServerIp, self.centralServerPort))
                    else:
                        self.terminal_printer("no other client right now please try in some time")


                if(b"sendquestion" in localCentralData):

                    questionAnswer=""
                    parsedMessage= self.parseIncomingMessage(localCentralData)
                    questionToAnswer=parsedMessage[2]
                    questionToAnswer=questionToAnswer[:len(questionToAnswer)-1].decode()
                    #print("hi")
                    self.terminal_printer("Here is the question for you")
                    self.terminal_printer(questionToAnswer)
                    #self.terminal_printer(parsedMessage[2])

                    while(self.inputData==""):
                        time.sleep(0.0001)

                    questionAnswer=self.inputData
                    self.clear_input_data()

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
                    self.clear_input_data()

                    replytoSend=""

                    if("yes" in questionAnswer.lower()):
                        replytoSend="ackanswer" + " <" + str(parsedMessage[1]) + ">"
                    else:
                        replytoSend="nakanswer" + " <" + str(parsedMessage[1]) + ">"

                    self.UDPClientCentralSocket.sendto(replytoSend.encode(),(self.centralServerIp, self.centralServerPort))
                    
                if(b"ackanswer" in localCentralData):
                    self.terminal_printer("Your Answer has been accepted, we will move forward with completing the connection!")
                    
                    #space here to code for getting ip map and public key
                    message= "sendcomreq" " <" + "for_me_is_client" + ">" + " <" + str(self.client_ip_address) +">"
                    encmessage=self.encrypt_data_central_server(message.encode())
                    
                    #self.UDPClientCentralSocket.sendto(encmessage, (self.centralServerIp, self.centralServerPort))
                    
                    #may be moved
                    
                    self.terminal_printer("congrats we are just doing final configs")
                    #print("now please use your textbox to send messages to your partner")
                    
                
                if(b"nakanswer" in localCentralData):
                    self.terminal_printer("Your answer has been rejected, please try from begining. Current session is terminated")
                    
                    message = "comfailed" + " <" + "client_is_not_me" + ">" + " <" + str(self.client_ip_address) + ">"
                    
                    encmessage=self.encrypt_data_central_server(message.encode())
                    self.UDPClientCentralSocket.sendto(encmessage, (self.centralServerIp, self.centralServerPort))
                    
                    #space here to code for more things
                    #may be moved
                    self.flagforServerConnection=False
                    self.flagForackcon=False
                    self.communicationFlag=False
                
                elif(b"refreshcom" in localCentralData):
                    pass
                 
                elif(b"sendcomreq" in localCentralData):
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
                    tempVar[0]=tempVar[0].strip()
                    tempVar[1]=int(tempVar[1])
                    tempVarArr.append(tempVar)
                    
                    print("ip port array:", tempVarArr)
                    self.forwarderServerIp=tempVar[0]
                    self.forwarderServerPort=tempVar[1]
                    
                    
                    self.relayServerIpporttupleList=tempVarArr
                    
                    for j in self.relayServerIpporttupleList:
                        self.relayServerIpList.append(j[0])
                        self.relayServerPortList.append(j[1])
                    
                    self.communicationFlag=True
                    print("stored ip-port")
                    self.terminal_printer("you can use your text box to communicate with your peer now!")
                        
                    
                localCentralData=""
        #sys.exit(self.app.exec_())
                    
                          

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
    client = Client(localIP, randPort, randPort2 )
    
    # we enter client program, everything beyond this point is coded inside the client class
    #client.run_program()
    #client.app.exec_()

main() # starting the program