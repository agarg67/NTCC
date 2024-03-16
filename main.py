import sys
import random
import time
import rsa
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from client_for_ui_integration import Client  # Adjusted to import the provided client


class ClientThread(QThread):
    updateSignal = pyqtSignal(str)

    def __init__(self, client, gui, *args, **kwargs):
        super().__init__()
        self.client = client
        self.args = args
        self.kwargs = kwargs
        self.gui = gui

    def run(self):
        run_program(self.client, self.gui)
        

class ClientGUI(QMainWindow):
    def __init__(self, client):
        super().__init__()
        self.initUI()
        self.client = client

    def initUI(self):
        self.setWindowTitle('Client GUI')
        self.setGeometry(100, 100, 800, 600)

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout()

        self.messageLog = QTextEdit()
        self.messageLog.setReadOnly(True)
        self.layout.addWidget(self.messageLog)

        self.inputBox = QLineEdit()
        self.layout.addWidget(self.inputBox)

        # Example for a "Send Command" button
        self.sendButton = QPushButton('Send')
        self.sendButton.clicked.connect(self.updateMessageLog)
        self.layout.addWidget(self.sendButton)

        self.centralWidget.setLayout(self.layout)

    def updateMessageLog(self):
        temp = str(self.inputBox.text())
        self.messageLog.append(temp)
        self.client.inputData = temp


def run_program(client_instance, gui_instance): # the whole communication of the program happens through here and so has a while true loop to prevent exit
        
        flagforServerConnection=True#will be made false
        
        while(flagforServerConnection==False):
            time.sleep(1)# will be changed 
        
        while(True):
            
            if(client_instance.inputData!="" and "CMD#?" in client_instance.inputData):
                client_instance.terminal_printer(client_instance.inputData)
                gui_instance.messageLog.append(client_instance.inputData)
                localInputData=client_instance.inputData
                client_instance.inputData=""

                ### The following if statements are bare-bone to purely test communication between client and server, will
                ### need to be changed to further continue sending messages to the server to store the information.
                if(client_instance.localInputData=="CMD#?reqcon"):
                    message="reqcon"
                    message_bytes = message.encode('ascii')
                    client_instance.UDPClientCentralSocket.sendto(message_bytes,(client_instance.centralServerIp, client_instance.centralServerPort)) # will be changed according to central server ip


            elif(client_instance.inputData!=""):
                client_instance.terminal_printer(client_instance.inputData)
                gui_instance.messageLog.append(client_instance.inputData)
                localInputData=client_instance.inputData
                client_instance.inputData=""
                
                if(localInputData=="sendpubip"):
                    client_instance.sendPublickeyIP()
                    
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
                        
                        
                    
                    
                
            if(client_instance.relayData!=""):
                client_instance.terminal_printer(client_instance.relayData)
                gui_instance.messageLog.append(client_instance.relayData)
                localRelayData=client_instance.relayData[0]
                localRelayAddr=client_instance.relayData[1]
                client_instance.relayData=""
                
                if(b"dataSent" in localRelayData): # will be changed
                    message="gotMessage"
                    client_instance.UDPClientRelaySocket.sendto(message.encode(), localRelayAddr)
                
            if(client_instance.centralData!=""):
                client_instance.terminal_printer(client_instance.centralData)
                gui_instance.messageLog.append(client_instance.centralData)
                localCentralData=client_instance.centralData[0]
                localaddr=client_instance.centralData[1]
                client_instance.centralData=""
                
                if(b"ackcon" in localCentralData):
                    client_instance.terminal_printer("public key sent to server")
                    gui_instance.messageLog.append("public key sent to server")
                    parsedDataArr=client_instance.parseIncomingMessage(localCentralData)
                    client_instance.terminal_printer(parsedDataArr)
                    gui_instance.messageLog.append(parsedDataArr)
                    
                    client_instance.publickeyserver=parsedDataArr[1]
                    
                    messagetoenc=b"hello"
                    encmessage=rsa.encrypt(messagetoenc, client_instance.publickeyserver)
                    client_instance.terminal_printer("test encryption:")
                    gui_instance.messageLog.append("test encryption:")
                    client_instance.terminal_printer(encmessage)
                    gui_instance.messageLog.append(encmessage)
                    
                    
                    
                    client_instance.terminal_printer("please enter your question:")
                    gui_instance.messageLog.append("please enter your question:")
                    while(client_instance.inputData==""):
                        time.sleep(0.0001)
                    
                    question=client_instance.inputData
                    client_instance.inputData=""
                    
                    client_instance.terminal_printer("Please enter your answer:")
                    gui_instance.messageLog.append("Please enter your answer:")
                    
                    while(client_instance.inputData==""):
                        time.sleep(0.0001)
                        
                    answer=client_instance.inputData
                    client_instance.inputData=""
                    
                    client_instance.sendQuestionToServer(question, answer)
                    
                    
                    
                
                if(b"sendquestion" in localCentralData):
                    
                    questionAnswer=""
                    parsedMessage= client_instance.parseIncomingMessage(localCentralData.decode())
                    client_instance.terminal_printer(parsedMessage[2])
                    gui_instance.messageLog.append(parsedMessage[2])
                    
                    while(client_instance.inputData==""):
                        time.sleep(0.0001)
                    
                    questionAnswer=client_instance.inputData
                    client_instance.inputData=""
                    
                    client_instance.answerQuestion(parsedMessage[1], questionAnswer)
                    
                if(b"answerquestion" in localCentralData):
                    acceptOrReject="No"
                    
                    parsedMessage = client_instance.parseIncomingMessage(localCentralData)
                    
                    client_instance.terminal_printer("Recieved the following answer:")
                    client_instance.terminal_printer(parsedMessage[2])
                    client_instance.terminal_printer("reply yes to accept, reply with anything else to reject")
                    gui_instance.messageLog.append("Recieved the following answer:")
                    gui_instance.messageLog.append(parsedMessage[2])
                    gui_instance.messageLog.append("reply yes to accept, reply with anything else to reject")
                    
                    questionAnswer=""
                    while(client_instance.inputData==""):
                        time.sleep(0.0001)
                    
                    questionAnswer=client_instance.inputData
                    client_instance.inputData=""
                    
                    replytoSend=""
                    
                    if("yes" in questionAnswer.lower()):
                        replytoSend="ackanswer" + " <" + str(parsedMessage[1]) + ">"
                    else:
                        replytoSend="nakanswer" + " <" + str(parsedMessage[1]) + ">"
                    
                    client_instance.UDPClientCentralSocket.sendto(replytoSend.encode(),(client_instance.centralServerIp, client_instance.centralServerPort))
                    
                if(b"ackanswer" in localCentralData):
                    client_instance.terminal_printer("Your Answer has been accepted, we will move forward with completing the connection!")
                    gui_instance.messageLog.append("Your Answer has been accepted, we will move forward with completing the connection!")
                    
                    #space here to code for getting ip map and public key
                
                if(b"nakanswer" in localCentralData):
                    client_instance.terminal_printer("Your answer has been rejected, please try from begining. Current session is terminated")
                    gui_instance.messageLog.append("Your answer has been rejected, please try from begining. Current session is terminated")
                    
                    #space here to code for more things
                localCentralData=""



def main():

    app = QApplication(sys.argv)
    gui = ClientGUI(mainClient)
    gui.show()  

    gui.messageLog.append("central port:" + str(randPort))
    gui.messageLog.append("relay port:" + str(randPort2))
    gui.messageLog.append(str(localIP))
    gui.messageLog.append(str(mainClient.publicKeySelf))
    gui.messageLog.append(str(mainClient.privatekeySelf))


    mainClientThread = ClientThread(mainClient, gui)
    mainClientThread.start()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    #fetching the ip address here
    localIP=Client.get_local_ip() 
    
    #setting ports for socket communication
    randPort=random.randrange(1500, 50000, 1)
    
    randPort2=random.randrange(1500, 50000, 1)
    
    while(randPort2==randPort):
        randPort2=random.randrange(1500, 50000, 1)

    mainClient = Client(localIP, randPort, randPort2)  # Assuming the Client class has necessary initialization parameters
    main()
