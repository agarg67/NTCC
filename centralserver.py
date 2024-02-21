import sys
import os
import socket
import hashlib
import struct
import re
import pickle
import random
import threading
import time
import rsa

''' 
    Should have the central server send it's messages to the relay server rather than directly send it to other clients, 
    as that is an initial point of weakness since the messages can be traced to each client due to the same point of 
    initial contact.
'''
class CentralServer:

    # Vital Parameters for the Central Server
    localIP = "127.0.0.1"
    localPort = 20001
    bufferSize = 1024

    #will change this to a hashmap/dictionary for better performance
    received_messages = []

    active_clients = list()
    public_keys = list()  ### For now we can store it in a list, later we can find a more secure way to store it ###
    questions = list()
    answers = list()

    def __init__(self):
        #self.rsaPublicKey = None
        #self.rsaPrivateKey = None
        self.inputData = None
        self.UDPserver = None
        self.Client = None
        self.threadInput = None
        self.threadClient = None
        self.threadUDPserver = None
        self.active_clients.clear()
        self.createSocket()
        print("Central Server Initialized : {}:{}".format(self.fetch_ip_address(), self.localPort))

    def fetch_ip_address(self):
        ip_address = ''
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
        except socket.timeout as e:
            print("The Socket has timed out: {}".format(e))
        except socket.gaierror as e:
            print("The Socket has encountered an error trying to fetch IP information: {}".format(e))
        except socket.error as e:
            print("Socket Input and Output error: {}".format(e))
        finally:
            s.close()
        return ip_address

    def createSocket(self):
        self.threadInput = threading.Thread(target=self.getAsynchrounous_input)
        self.threadInput.daemon = True
        self.threadInput.start()

        self.UDPserver = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
        self.UDPserver.bind(('', self.localPort))

        self.threadUDPserver = threading.Thread(target=self.getUDPserver_input)
        self.threadUDPserver.daemon = True
        self.threadUDPserver.start()

        print("Current system: ", os.name)
        if (os.name == "posix"):
            self.UDPserver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        else:
            self.UDPserver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def rsa_keyGen(self):
        self.rsaPublicKey, self.rsaPrivateKey = rsa.newkeys(1024)
        #print(self.rsaPublicKey)
        #print(self.rsaPrivateKey)
        if (self.rsaPublicKey and self.rsaPrivateKey) is not None:
            return True
        return False

    def getAsynchrounous_input(self):
        while True:
            self.inputData = input()

    def getUDPserver_input(self):
        while True:
            data, addr = self.UDPserver.recvfrom(self.bufferSize)
            self.receive_message(data, addr)

    def getClient_input(self):
        while True:
            data, addr = self.Client.recvfrom(self.bufferSize)
            self.receive_message(data, addr)

    def parse_message(self, data, addr):

        #keyLength = int.from_bytes(4, 'big')

        # Receive the key itself
        #publicKeyBytes = b''
        #while len(publicKeyBytes) < keyLength:
        #    publicKeyBytes += keyLength - len(publicKeyBytes)


        # Reconstruct the public key object
        #publicKey = pickle.loads(publicKeyBytes)

        #print(publicKey)

        #addr = "68.99.192.233"

        print("This is the data received: {}".format(data))
        print("\nThis is the data received from: {}".format(addr))

        #original_message = data.decode()
        message_identifier = data.split(b" <")

        print(message_identifier)

        if message_identifier[0] == b"sendpubip":
            self.active_clients.append(addr)
            message_identifier[1] = message_identifier[1].replace(b">", b"")
            print(message_identifier[1])

            #public_key = pickle.loads(bytes(message_identifier[1]))

            self.public_keys.append(message_identifier[1])
            #print("Public Key received")


            #print(self.rsaPublicKey)

            publicKeyBytes = pickle.dumps(self.rsaPublicKey)
            message = b"ackcon" + b" <" + publicKeyBytes + b"> <" + (str(self.active_clients[0][0])).encode() + b">"

            print(message)

            self.UDPserver.sendto(message, addr)


            #message = "ackcon" + " <" + str(self.rsaPublicKey) + "> "
            #self.UDPserver.sendto(message.encode(), addr)

            #print("#######################################")
            #print(self.rsaPublicKey)
            #print("\n" + self.public_keys[0])


            #test_message = "THIS IS A TEST".encode('latin')
            #ciphertext = rsa.encrypt(test_message, public_key)
            #print(ciphertext)
            #ciphertext = rsa.encrypt(test_message, self.rsaPublicKey)
            #print(ciphertext)

        elif message_identifier[0] == "sendquestion":
            print("Question received from Client with {}".format(addr))
            ##WOULD NEED TO KNOW THE FORMAT OF THE QUESTION MESSAGE
            self.questions.append(message_identifier[1])
            message = "ackquestion" + " <" + message_identifier[2] + "> "#This will be the question ID received
            self.UDPserver.sendto(message.encode(), addr)

        elif message_identifier[0] == "answerquestion":
            print("Answer received from User")
            ##NEED To REPLACE WITH FORMAT

        elif message_identifier[0] == "comrequest":
            print("Client has requested to communicate with another client. Fetching active clients list:")
            print(self.active_clients[:])
        else:
            print("Message not recognized")
            return None

    def initiate_communication(self, data, addr):
        ### Checks if there is two clients simultaneously requesting to communicate ###
        print(self.active_clients)

        print("Error: No other client is requesting to communicate")
        # if active_clients[0][0] != active_clients[1][0]:
        #    print("Two clients have requested to communicate with each other")
        #     print("Client {} and Client {} are trying to communicate".format(active_clients[0], active_clients[1]))

    #### Helper functions to store the data from the client ####
    ## Will need more information as to how to maintain the ordering of the UDP packets in order to store the data correctly ##
    def store_public_key(self, data, addr):
        self.public_keys.append(data)

    def store_question(self, data, addr):
        self.questions.append(data)

    def store_answer(self, data, addr):
        self.answers.append(data)

    def receive_message(self, data, addr):

        message_hash = hashlib.sha256(data).hexdigest()

        '''
        if not self.received_messages:
            self.received_messages.append([addr, message_hash])
            print("Received Message: \n{} \nfrom {}".format(data.decode(), addr))
        else:
            for address, message in self.received_messages:
                if address[0] == addr[0] and message == message_hash:
                    print("Original message: ", message)
                    print("Message hash: ", message_hash)
                    print("Message already received from same IP address. Ignoring message.")
                    return
            print("Received Message: \n{} \nfrom {}".format(data.decode(), addr))
            print("Message hash: ", message_hash)
            '''
        self.received_messages.append([addr, message_hash])
        self.parse_message(data, addr)

    def startup(self):
        self.rsa_keyGen()
        numFailures = 0


        while True:
            #localInput = self.inputData
            #self.inputData = ""
            data, address = self.UDPserver.recvfrom(self.bufferSize)



            if self.rsa_keyGen():
                numFailures=0
                self.receive_message(data, address)
            else:
                numFailures+=1
                print("\nServer has failed to generate RSA keys, retrying...")
                if numFailures == 10:
                    print("\nCentral Server is unable to generate RSA keys, aborting all operations.")
                    exit(42)
            start = time.perf_counter()
            print("Socket has been open for {} seconds".format(time.perf_counter()-start))
            #self.UDPserver.timeout(2)

    #################################### HELPER FUNCTIONS FOR SERVER ###########################################
    ### A Keep alive protocol that ensures a client is still active ###
    #def _keep_alive(self):
    #    while True:
    #        time.sleep(50)
    #        UDPserver.sendto("Are you still there?".encode('ascii'), ('', localPort))

    #def _reset_UDP_server(self):
    #    UDPserver.close()
    #    self.__init__()
    #    main()

    ### Pickle will be used to transport the list of IPs to the forwarder ###
    #def package_constructor(self):
        # pickled_data = pickle.dumps(ip_addresses)
        ### Only the forwarder should receive the pickled data, and should never be shared with the client besides the
        # forwarder ip_address ###
    #    return 0  # pickled_data

    ##########################################################################################################



def main():
    server = CentralServer()
    server.startup()

if __name__ == "__main__":
    print(os.name)
    main()