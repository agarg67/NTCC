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
        self.createSocket()  # Start sockets and threads as part of initialization

    def createSocket(self):
        self.UDPClientCentralSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPClientCentralSocket.bind((self.client_ip_address, self.clientCentralPort))
        
        self.UDPClientRelaySocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPClientRelaySocket.bind((self.client_ip_address, self.clientRelayPort))
        
        # Start threads for handling data
        self.threadCentral = threading.Thread(target=self.fetch_data_central)
        self.threadCentral.daemon = True
        self.threadCentral.start()
        
        self.threadRelay = threading.Thread(target=self.fetch_data_relay)
        self.threadRelay.daemon = True
        self.threadRelay.start()

    def fetch_data_central(self):
        while True:
            try:
                data, addr = self.UDPClientCentralSocket.recvfrom(self.bufferSize)
                print(f"Data received from central server: {data.decode()}")
                self.centralData = data.decode()
                # Additional processing can be added here
            except Exception as e:
                print(f"Error receiving data from central server: {e}")

    def fetch_data_relay(self):
        while True:
            try:
                data, addr = self.UDPClientRelaySocket.recvfrom(self.bufferSize)
                print(f"Data received from relay: {data.decode()}")
                self.relayData = data.decode()
                # Additional processing can be added here
            except Exception as e:
                print(f"Error receiving data from relay: {e}")

    def handle_command(self, command):
        print(f"Processing command: {command}")
        # Example command processing
        if command == "send_public_key":
            self.send_public_key()
        # Add more command handlers as needed

    def send_public_key(self):
        # Example of sending the public key; adjust logic as needed for your application
        message = f"Public Key: {self.publicKeySelf.exportKey()}"
        self.UDPClientCentralSocket.sendto(message.encode(), (self.centralServerIp, self.centralServerPort))
        print("Public key sent to central server.")

def start_client(centralServerIp, centralServerPort):
    localIP = get_local_ip()
    randPort = random.randrange(1500, 50000)
    randPort2 = randPort
    while randPort2 == randPort:
        randPort2 = random.randrange(1500, 50000)
    
    client = Client(localIP, randPort, randPort2)
    client.centralServerIp = centralServerIp
    client.centralServerPort = centralServerPort

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def main():
    centralServerIp = 'localhost'
    centralServerPort = 20001
    start_client(centralServerIp, centralServerPort)

if __name__ == "__main__":
    main()
