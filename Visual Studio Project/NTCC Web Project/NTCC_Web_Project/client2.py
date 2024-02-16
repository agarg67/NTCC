import socket
import random
import threading
import rsa
import time

class Client:
    
    def __init__(self, ipPass, portPass, portPass2):
        self.client_ip_address = ipPass
        self.clientCentralPort = portPass
        self.clientRelayPort = portPass2
        self.publicKeySelf, self.privateKeySelf = rsa.newkeys(2048)
        self.centralServerIp = "localhost"
        self.centralServerPort = 20001  # Example default, can be overridden
        self.inputData = ""
        self.centralData = ""
        self.relayData = ""
        self.bufferSize = 4096
        self.questionId = random.randrange(1001, 20000, 4)
        self.messageId = random.randrange(2001, 30000, 5)
        # Additional initialization as needed...

    def createSocket(self):
        # Socket creation and thread starting logic...
        self.UDPClientCentralSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPClientCentralSocket.bind((self.client_ip_address, self.clientCentralPort))

        self.UDPClientRelaySocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPClientRelaySocket.bind((self.client_ip_address, self.clientRelayPort))
        
        # Thread for asynchronous input
        self.threadInput = threading.Thread(target=self.asynchronous_input)
        self.threadInput.daemon = True
        self.threadInput.start()

        # Additional threads for handling central and relay data...
    
    def asynchronous_input(self):
        while True:
            self.inputData = input("Enter command: ")
            # Processing input data...

    def start(self):
        self.createSocket()
        # Potentially other start-up operations...

# Function to start the client, called from Flask app
def start_client(centralServerIp, centralServerPort):
    localIP = get_local_ip()
    randPort = random.randrange(1500, 50000)
    randPort2 = randPort
    while randPort2 == randPort:
        randPort2 = random.randrange(1500, 50000)
    
    client = Client(localIP, randPort, randPort2)
    client.centralServerIp = centralServerIp
    client.centralServerPort = centralServerPort
    client.start()

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))  # Use an address in the subnet
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == "__main__":
    # This part is for direct script execution, and might be adjusted based on your specific needs
    centralServerIp = 'localhost'  # Example IP, adjust as needed
    centralServerPort = 20001  # Example port, adjust as needed
    start_client(centralServerIp, centralServerPort)
