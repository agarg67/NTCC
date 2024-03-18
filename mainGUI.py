import sys
import random
import time
import rsa
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QThread, pyqtSignal

class ClientGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.currentCommand = ""

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
        self.sendButton.clicked.connect(self.updateCommand)
        self.layout.addWidget(self.sendButton)

        self.centralWidget.setLayout(self.layout)

    def updateCommand(self):
        temp = str(self.inputBox.text())
        self.inputBox.text = ""
        self.currentCommand = temp

    def getCommand(self):
        return self.currentCommand
        