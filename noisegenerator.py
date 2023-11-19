import sys
import os
import socket
import re
import pickle
import random
import threading
import time

localPort = 8080

NoiseGeneratorServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)


class NoiseGenerator:
    HOST = ""
    PORT = 0

    bufferSize = 4096

    def _getIP_address(self):
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

    def __init__(self):
        self.HOST = self._getIP_address()
        self.PORT = localPort
        NoiseGeneratorServer.bind(('', localPort))
        NoiseGeneratorServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        NoiseGeneratorServer.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def dynamicallyIPForwading(data, addr):
        ## This function will be used to dynamically forward the data to the next server and eventually the client. ##
        try:
            if data.decode() == "ackreceiveipmapper":
                ipaddress = map()
                pickled_message = pickle.dumps(ipaddress)
        except Exception as e:
            print("Failed in Dynamically IP Forwarding: {}".format(e))
        finally:
            NoiseGeneratorServer.sendto(pickled_message, addr)

    ## Will clone the received message, regardless from client or not ##
    def cloneClientMessage(self):
        ## Will need a priority or queue system to determine which message to clone first, otherwise we risk just
        # cloning same message over and over again ##
        pass

    def startNoiseGeneration(self):
        while True:
            data, addr = NoiseGeneratorServer.recvfrom(self.bufferSize)
            if not data:
                break
            self.dynamicallyIPForwading(data, addr)
            NoiseGeneratorServer.sendto(data, addr)
            print(data)  # For testing purposes
            print(addr)

    # The server can't utilize listen function as that requires a TCP socket, which inevitably leaks the ip_address of
    # the client. #

    # def startPortForward(localPort, remoteHost, remotePort):
    #    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #    server.bind(('localHost', localPort))
    #    server.listen(1)
    #    print("forwarding from localHost {localPort} to {remoteHost}: {remotePort}")

    #        while True:
    #            localSocket, localAddr = server.accept()

    #            print("accepted connection")

    #            remoteSocket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    #            remoteSocket.connect(('localhost', remotePort))
    #
    #            forwardRemote = threading.Thread(target = forwarder, args = (localSocket, remoteSocket))
    #            forwardlocal = threading.Thread(target = forwarder, args = (remoteSocket, localSocket))

    #            forwardRemote.start()
    #            forwardlocal.start()

    if __name__ == "__main__":
        __init__()
        startNoiseGeneration()
