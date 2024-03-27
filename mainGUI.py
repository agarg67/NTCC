import sys
import random
import time
import rsa
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import QThread, pyqtSignal

class ClientGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.currentCommand = ""
        self.initUI()
        

    def initUI(self):
        self.setWindowTitle('Client GUI')
        self.setGeometry(100, 100, 800, 600)

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout()

        self.messageLog = QTextEdit()
        self.cursor = QTextCursor(self.messageLog.textCursor())
        self.messageLog.setReadOnly(True)
        self.layout.addWidget(self.messageLog)

        
        #Server Buttons
        self.serverButtonLayout = QHBoxLayout()

        self.sendpubip_Button = QPushButton('sendpubip')
        self.sendpubip_Button.clicked.connect(lambda: self.setCommand(input = "sendpubip"))
        self.disconnectServer_Button = QPushButton('disconnectServer')
        self.disconnectServer_Button.clicked.connect(lambda: self.setCommand(input = "disconnectServer"))
        
        self.serverButtonLayout.addWidget(self.sendpubip_Button)
        self.serverButtonLayout.addWidget(self.disconnectServer_Button)

        self.layout.addLayout(self.serverButtonLayout)

        
        #Communication Buttons
        self.comButtonLayout = QHBoxLayout()

        self.sendcomreq_Button = QPushButton('sendcomreq')
        self.sendcomreq_Button.clicked.connect(lambda: self.setCommand(input = "sendcomreq"))
        self.comrequest_Button = QPushButton('comrequest')
        self.comrequest_Button.clicked.connect(lambda: self.setCommand(input = "comrequest"))
        self.refreshcom_Button = QPushButton('refreshcom')
        self.refreshcom_Button.clicked.connect(lambda: self.setCommand(input = "refreshcom"))

        self.comButtonLayout.addWidget(self.sendcomreq_Button)
        self.comButtonLayout.addWidget(self.comrequest_Button)
        self.comButtonLayout.addWidget(self.refreshcom_Button)

        self.layout.addLayout(self.comButtonLayout)


        #Acknowledge Buttons
        self.ackButtonLayout = QHBoxLayout()
       
        self.ackcon_Button = QPushButton('ackcon')
        self.ackcon_Button.clicked.connect(lambda: self.setCommand(input = "ackcon"))
        self.ackquestion_Button = QPushButton('ackquestion')
        self.ackquestion_Button.clicked.connect(lambda: self.setCommand(input = "ackquestion"))
        self.ackanswer_Button = QPushButton('ackanswer')
        self.ackanswer_Button.clicked.connect(lambda: self.setCommand(input = "ackanswer"))
        
        self.ackButtonLayout.addWidget(self.ackcon_Button)
        self.ackButtonLayout.addWidget(self.ackquestion_Button)
        self.ackButtonLayout.addWidget(self.ackanswer_Button)

        self.layout.addLayout(self.ackButtonLayout)


        #Question Buttons
        self.questionButtonLayout = QHBoxLayout()
        
        self.sendquestion_Button = QPushButton('sendquestion')
        self.sendquestion_Button.clicked.connect(lambda: self.setCommand(input = "sendquestion"))
        self.answerquestion_Button = QPushButton('answerquestion')
        self.answerquestion_Button.clicked.connect(lambda: self.setCommand(input = "answerquestion"))
        
        self.questionButtonLayout.addWidget(self.sendquestion_Button)
        self.questionButtonLayout.addWidget(self.answerquestion_Button)
        
        self.layout.addLayout(self.questionButtonLayout)


        #Input Box when needed
        self.inputBox = QLineEdit()
        self.layout.addWidget(self.inputBox)

        # Example for a "Send Command" button
        self.sendButton = QPushButton('Send')
        self.sendButton.clicked.connect(self.updateCommand)
        self.layout.addWidget(self.sendButton)

        self.centralWidget.setLayout(self.layout)

    def updateCommand(self):
        #print(self.inputBox.text())
        temp = str(self.inputBox.text())
        self.inputBox.clear()
        self.currentCommand = temp

    def getCommand(self):
        temp=self.currentCommand
        #self.currentCommand=""
        return temp
    
    def setCommand(self, input):
        self.currentCommand = input