import queue
import sys
import os
import socket
import re
import pickle
import random
import threading
import time


class Relay:
    server=""
    serverport=0

    messages = queue.Queue()
    client = []
    

    def __init__(self, message, addr, portpass):
        self.server = addr
        self.serverport = portpass


    def recieve(self):
        while True:
            try:
                message ,_ = server.recvfrom(2048)
                self.messages.put(message)
            except:
                pass

    def relay(self):
        while not messages.empty():
            message = self.messages.get()

            server.sendto(message, ("127.0.0.1", 20001)) #subject to change


    def run_program(self):
        t1 = threading.Thread(target=recieve)
        t2 = threading.Thread(target=relay)

def main():
    reciever = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    reciever.bind(("localhost", 9999))
    message, addr, port = reciever.recvfrom(2048)
    relay = Relay(message, addr, port)

    Relay.run_program()

main()
