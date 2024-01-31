import queue
import sys
import os
import socket
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

class Forwarder:
    HOST = ""
    PORT = 0
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("localhost", 9999))
messages = queue.Queue()
client = []
def recieve():
    while True:
        try:
            message ,_ = server.recvfrom(2048)
            messages.put(message)
        except:
            pass

def relay():
    while not messages.empty():
        message = messages.get()

        server.sendto(message, ("127.0.0.1", 20001)) #subject to change

t1 = threading.Thread(target=recieve)
t2 = threading.Thread(target=relay)
