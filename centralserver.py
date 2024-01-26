import sys
import os
import socket
import struct
import re
import pickle
import random
import threading
import time

class IP_mapper: 
    ip_address1=""
    ip_address2=""
    port1=0
    port2=0
    
    def __init__(self, ip1, ip2, p1, p2):
        self.ip_address1=ip1
        self.ip_address2=ip2
        self.port1=p1
        self.port2=p2

# Parameters for the central server
localIP = "127.0.0.1"  ## Will change accordingly to the IP address of the Raspberry Pi connected to different networks
localPort = 20001
bufferSize = 1024

### Parameters for the forwarder server ###
ForwarderIP = ""
ForwarderPort = 0

InitiateCommunication = False

### Keeps a list of tracked messages ids ###
received_messages = []

#ip_addresses = map()

active_clients = list()
public_keys = list() ### For now we can store it in a list, later we can find a more secure way to store it ###
questions = list()
answers = list()

UDPserver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#################################### HELPER FUNCTIONS FOR SERVER ###########################################
### A Keep alive protocol that ensures a client is still active ###
def _keep_alive():
    while True:
        time.sleep(50)
        UDPserver.sendto("Are you still there?".encode('ascii'), ('', localPort))

def _reset_UDP_server():
    UDPserver.close()
    __init__()
    main()

##########################################################################################################

def fetch_ip_address():
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

def __init__():
    global UDPserver
    active_clients.clear()
    UDPserver.bind(('', localPort))
    UDPserver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    UDPserver.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    ### A temporary timeout for the server in order to prevent it from running forever for testing purposes ###
    UDPserver.settimeout(500)  # Comment for infinite timeout

    print("Central Server Initialized : {}:{}".format(fetch_ip_address(), localPort))


def parse_message(data, addr):
    addr = "68.99.192.233"
    if data.decode() == "ackcon":
        print("Client from {} has successfully connected to the Server".format(addr))
        active_clients.append(addr)

    elif data.decode() == "comrequest":
        print("Client from {} has requested to communicate with another client".format(addr))
        #active_clients.append(('565.512.512.512', 20002)) ### Fake Client for testing purposes ###
        initiate_communication(data, addr)

    elif data.decode() == "ackpubip":
        print("Client from {} has sent their public key to the server".format(addr))
        if InitiateCommunication:
            store_public_key(data, addr)
        else:
            print(received_messages)
            received_messages.remove(received_messages[-1])
            print(received_messages)
            print("There is no client requesting to communicate.")

    elif data.decode() == "ackquestion":
        print("Client from {} has sent their question to the server".format(addr))
        store_question(data, addr)

    elif data.decode() == "ackanswer":
        print("Client from {} has sent their answer to the server".format(addr))
        store_answer(data, addr)

    elif data.decode() == "ackdis":
        print("Client from {} has disconnected from the server".format(addr))
        _reset_UDP_server()

    else:
        print("Message not recognized")
        return None

def initiate_communication(data, addr):
    ### Checks if there is two clients simultaneously requesting to communicate ###
        print(active_clients)

        print("Error: No other client is requesting to communicate")
        #if active_clients[0][0] != active_clients[1][0]:
        #    print("Two clients have requested to communicate with each other")
       #     print("Client {} and Client {} are trying to communicate".format(active_clients[0], active_clients[1]))
        global InitiateCommunication
        InitiateCommunication = True

#### Helper functions to store the data from the client ####
## Will need more information as to how to maintain the ordering of the UDP packets in order to store the data correctly ##
def store_public_key(data, addr):
    public_keys.append(data)

def store_question(data, addr):
    questions.append(data)

def store_answer(data, addr):
    answers.append(data)


def receive_message(data, addr):
    message_bytes = bytes(data.decode(), 'ascii')
    message_id = struct.unpack('!I', message_bytes[:4])[0]
    print(message_id)

    ### Checks if the message has already been received before ###
    if message_id in received_messages:
        print("Message already received")
        pass
    else:
        received_messages.append(message_id)
        parse_message(data, addr)
        print(message_bytes)  ### For testing purposes ###


def main():
    print("Timer has started for 2 minutes")
    while True:
        time1 = time.perf_counter()
        time2 = time.perf_counter()
        if time2 - time1 > 10:
            print("Timer has ended")
            break
        else:
            data, addr = UDPserver.recvfrom(bufferSize)
            receive_message(data, addr)
            addr = "68.99.192.233"
            print("received message: {} from {}".format(data, addr)) ### For testing purposes ###
            print("Timer has started for 2 minutes")


    print("Timer has ended")

### Pickle will be used to transport the list of IPs to the forwarder ###
def package_constructor():
    pickled_data = pickle.dumps(ip_addresses)
    ### Only the forwarder should receive the pickled data, and should never be shared with the client besides the
    # forwarder ip_address ###
    return pickled_data

if __name__ == "__main__":
    __init__()
    main()
