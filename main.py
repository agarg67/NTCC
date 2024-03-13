import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QThread, pyqtSignal
from client_for_ui_integration import Client  # Adjusted to import the provided client


class ClientThread(QThread):
    updateSignal = pyqtSignal(str)

    def __init__(self, client_function, *args, **kwargs):
        super().__init__()
        self.client_function = client_function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        # Execute the client function passed during initialization
        # The function is expected to return a string message or raise an exception
        try:
            result = self.client_function(*self.args, **self.kwargs)
            self.updateSignal.emit(result)
        except Exception as e:
            self.updateSignal.emit(f"Error: {str(e)}")

class ClientGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        #fetching the ip address here
        localIP=Client.get_local_ip() 
        
        #setting ports for socket communication
        randPort=random.randrange(1500, 50000, 1)
        
        randPort2=random.randrange(1500, 50000, 1)
        
        while(randPort2==randPort):
            randPort2=random.randrange(1500, 50000, 1)
    
        print("central port:",randPort)
        print("relay port:",randPort2)
        print(localIP)

        self.client = Client(localIP, randPort, randPort2)  # Assuming the Client class has necessary initialization parameters
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Client GUI')
        self.setGeometry(100, 100, 600, 400)

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout()

        self.messageLog = QTextEdit()
        self.messageLog.setReadOnly(True)
        self.layout.addWidget(self.messageLog)

        self.connectButton = QPushButton('Connect')
        self.connectButton.clicked.connect(self.connectToServer)
        self.layout.addWidget(self.connectButton)

        self.centralWidget.setLayout(self.layout)

    def connectToServer(self):
        # This assumes the Client class has a method for connecting that returns a string status
        # You might need to adjust this based on the actual client implementation
        self.thread = ClientThread(self.client.connect_to_server)  # Adjust method name as needed
        self.thread.updateSignal.connect(self.updateMessageLog)
        self.thread.start()

    def updateMessageLog(self, message):
        self.messageLog.append(message)

def main():

    app = QApplication(sys.argv)
    gui = ClientGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
