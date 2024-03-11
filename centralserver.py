import sys
import os
import socket
import hashlib
import pickle
import threading
import time
import rsa
import signal

import json


class UDPServerSocketManager:
    def __init__(self):
        self.serverPort = 20001
        self.UDPserver = None

    def __enter__(self):
        self.UDPserver = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
        self.UDPserver.bind(('', self.serverPort))
        return self.UDPserver

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class ipMapper_manager:
    def __init__(self):
        # This will be a list of the IP addresses of the servers
        self.server_ips = ["123.412.321", "123.123.123", "123.123.123"]

    def __enter__(self):
        #self.server_ips.append()
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class CentralServer:

    def __init__(self):
        # Defining variables for the server:
        self.server_uptime = time.time()
        self.localPort = 20001
        self.bufferSize = 128000
        self.active_clients_and_keys = {}
        self.received_messages = {}
        self.questions_and_answer = {}
        self.threadUDPserver = None

        # forwarder information
        self.forwarderIP = None
        self.forwarderPublicKey = None

        # Instantiating Socket and IP address of the Server
        try:
            with UDPServerSocketManager() as socketobj:
                self.UDPserver = socketobj
        except socket.error as e:
            print(f"Error with the server socket: {e}")
        except (AttributeError, TypeError, OSError) as e:
            print(f"Error encountered with the Socket Manager class: {type(e), e}")
        print("Central Server Initialized : {}:{}".format(self.fetch_ip_address(), self.localPort))

    # Destructor that only closes the socket
    def __del__(self):
        self.UDPserver.close()
        pass

    # Fetches the IP address of the server
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

    # Creates a thread for the server to listen for incoming messages
    def createThread(self):
        self.threadUDPserver = threading.Thread(target=self.getUDPserver_input)
        self.threadUDPserver.daemon = True
        self.threadUDPserver.start()

    def rsa_keyGen(self):
        self.rsaPublicKey, self.rsaPrivateKey = rsa.newkeys(2048)
        if (self.rsaPublicKey and self.rsaPrivateKey) is not None:
            return True
        return False

    def getUDPserver_input(self):
        while True:
            data, addr = self.UDPserver.recvfrom(self.bufferSize)
            self.receive_message(data, addr)

    def message_identifier(self, data):
        message_identifier = data.split(b" <")
        return message_identifier[0]

    def main_message(self, data):
        main_message = data.split(b" <")
        main_message[1] = main_message[1].replace(b">", b"")
        return main_message[1]

    def message_sender(self, data):
        message_sender = data.split(b" <")
        message_sender[2] = message_sender[2].replace(b">", b"")
        return message_sender[2]

    def additional_message_editor(self, data):
        additional_message = data.split(b" <")
        additional_message[3] = additional_message[3].replace(b">", b"")
        return additional_message[3]


    # NEED To add a function that splits the message into 245 byte chunks and encrypts them separately
    def split_and_encrypt(self, message, client_public_key):

        whole_encrypted_message = None

        if (len(message) < 245):
            whole_encrypted_message = rsa.encrypt(message, client_public_key)
        else:
            for i in range(0, len(message), 245):
                message_chunk = message[i:i + 245]
                whole_encrypted_message = rsa.encrypt(message_chunk, client_public_key)

        return whole_encrypted_message

    # NEED To add a function that decrypts the message and combines the 245 byte chunks
    def split_and_decrypt(self, message):

        decrypted_message = None

        if (len(message) < 245):
            decrypted_message = rsa.decrypt(message, self.rsaPrivateKey)
        else:
            for i in range(0, len(message), 245):
                message_chunk = message[i:i + 245]
                decrypted_message += rsa.decrypt(message_chunk, self.rsaPrivateKey)

        return decrypted_message

    ## Apparently only the sendpubip and forwarder messages will be unecrypted, everything else will be assumed encrypted ##
    def parse_message(self, data, addr):

        print("This is the data received: {}".format(data))

        # Default values for all messages received
        identifier_flag = None
        source_ip = addr[0].encode()
        pem = self.rsaPublicKey.save_pkcs1()
        server_ip = self.fetch_ip_address().encode()

        if (b"sendpubip" in data) or (b"forwarder" in data):
            identifier_flag = self.message_identifier(data)
            message_content = self.main_message(data)
            message_sender = self.message_sender(data)

        if identifier_flag == b"sendpubip":

            client_public_key = rsa.PublicKey.load_pkcs1(message_content.decode())

            # Need the address to be in bytes in order to be compared with the message_sender
            if source_ip == message_sender:
                if message_sender not in self.active_clients_and_keys:
                    self.active_clients_and_keys.setdefault(message_sender, client_public_key)
                    message = (b"ackcon <" + pem + b"> <" + server_ip + b">")

                    temp_message = []
                    temp_message.append(message[0:245])
                    temp_message.append(message[245:])

                    print(temp_message)

                    print(len(message))

                    #message = b"hey"
                    encrypted_message = rsa.encrypt(temp_message[0], client_public_key)
                    encrypted_message2 = rsa.encrypt(temp_message[1], client_public_key)
                    print(len(encrypted_message + encrypted_message2))
                    #encrypted_message = rsa.encrypt(message, client_public_key)

                    self.UDPserver.sendto(encrypted_message + encrypted_message2, addr)

                # Updates a client's public key if the client is already in the dictionary
                elif message_sender in self.active_clients_and_keys:
                    self.active_clients_and_keys[message_sender] = client_public_key
                    message = (b"ackcon <" + pem + b"> <" + server_ip + b">")
                    self.UDPserver.sendto(message, addr)
            else:
                print("Connection denied {} due to wrong IP address in the message {}".format(addr, message_sender))

        elif identifier_flag == b"forwarder":

            if source_ip == message_sender:
                self.forwarderIP = source_ip
                self.forwarderPublicKey = rsa.PublicKey.load_pkcs1(message_content.decode())

                message = (b"ackforwarder <" + pem + b"> <" + server_ip + b">")
                self.UDPserver.sendto(message, addr)
            else:
                print("Forwarder connection denied from {}.".format(addr))

        else:

            if source_ip == self.forwarderIP:

                ip_map = ipMapper_manager()

                if not self.forwarderPublicKey:
                    print("Forwarder has not sent their public key")
                else:
                    ciphertext = data
                    decrypted_message = rsa.decrypt(ciphertext, self.rsaPrivateKey)

                    identifier_flag = self.message_identifier(decrypted_message)
                    message_content = self.main_message(decrypted_message)
                    message_sender = self.message_sender(decrypted_message)

                    if identifier_flag == b"sendipmapper":

                        key_phrase = b"Central_Server598135_4123.512356"

                        if (message_content == key_phrase) and (source_ip == message_sender):

                            #temp = json.dumps(server_ips).encode('utf-8')
                            #print(temp)

                            temp = json.dumps(ip_map.server_ips).encode('utf-8')
                            print(temp)

                            message = (b"ackipmapper <" + temp + b"> <" + server_ip + b">")
                            print(message)

                            encrypted_message = rsa.encrypt(message, self.forwarderPublicKey)
                            print(encrypted_message)

                            self.UDPserver.sendto(encrypted_message, addr)
                        else:
                            print("Forwarder has sent an incorrect key phrase or IP address")

            elif source_ip in self.active_clients_and_keys:

                if not self.active_clients_and_keys[source_ip]:
                    print("Client {} has not sent their public key".format(addr))
                else:

                    ciphertext = data
                    decrypted_message = rsa.decrypt(ciphertext, self.rsaPrivateKey)

                    identifier_flag = self.message_identifier(decrypted_message)
                    message_content = self.main_message(decrypted_message)
                    message_sender = self.message_sender(decrypted_message)

                    if identifier_flag == b"sendquestion":

                        question = message_sender
                        answer = self.additional_message_editor(decrypted_message)

                        if not self.questions_and_answer:
                            self.questions_and_answer.setdefault(addr, [question, answer])
                        elif source_ip in self.questions_and_answer:

                            if self.questions_and_answer[addr[0].encode()] != [question, answer]:
                                self.questions_and_answer[addr[0].encode()] = [question, answer]
                            # Probably redundant
                            elif question or answer not in self.questions_and_answer[addr[0].encode()]:
                                self.questions_and_answer[addr[0].encode()] = [question, answer]

                        print(b"THIS IS THE QUESTION RECEIVED:" + question + b"\nTHIS IS THE ANSWER RECEIVED:" + answer)

                        message = (b"ackquestion" + b" <" + message_content + b"> <"
                                   + str(self.fetch_ip_address()).encode() + b">")

                        print(message)

                        encrypted_message = rsa.encrypt(message, self.active_clients_and_keys[source_ip])

                        print(encrypted_message)

                        self.UDPserver.sendto(encrypted_message, addr)









            else:
                print("Client {} is not in the active clients list".format(addr))

        """
        elif identifier_flag == b"sendquestion":

            temp_message = []
            temp_message = data.split(b" <")
            temp_message[1] = temp_message[1].replace(b">", b"")
            temp_message[2] = temp_message[2].replace(b">", b"")
            temp_message[3] = temp_message[3].replace(b">", b"")

            print(temp_message)


            if message_sender in self.active_clients_and_keys:

                if not self.active_clients_and_keys[message_sender]:
                    print("Client {} has not sent their public key".format(message_sender))

                else:
                    ciphertext = pickle.loads(message_content)
                    decrypted_message = rsa.decrypt(ciphertext, self.rsaPrivateKey)
                    print("Decrypted message: {}".format(decrypted_message))


            else:
                print("Client {} is not in the active clients list".format(message_sender))




            pass
        elif identifier_flag == b"answerquestion":
            pass
        elif identifier_flag == b"comrequest":
            pass
        """


        message_identifier = data.split(b" <")


        if message_identifier[0] == b"sendpubip":
            pass

        elif message_identifier[0] == "sendquestion":
            print("Question received from Client with {}".format(addr))
            ##WOULD NEED TO KNOW THE FORMAT OF THE QUESTION MESSAGE
            self.questions.append(message_identifier[1])
            message = "ackquestion" + " <" + message_identifier[2] + "> "  # This will be the question ID received
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

    def receive_message(self, data, addr):

        message_hash = hashlib.sha256(data).hexdigest()

        if not self.received_messages:
            self.received_messages = {addr: [message_hash]}
            self.parse_message(data, addr)
        elif (addr in self.received_messages) and (message_hash in self.received_messages[addr]):
            print("Duplicate message received, discarding...")
        elif (addr in self.received_messages) and (message_hash not in self.received_messages[addr]):
            self.received_messages[addr].append(message_hash)
            self.parse_message(data, addr)
        elif addr not in self.received_messages:
            self.received_messages.setdefault(addr, [message_hash])
            self.parse_message(data, addr)

        print(self.received_messages)

    # Calulates the time for the server to refresh
    def countdown_timer_server_refresh(self, seconds):
        return self.server_uptime + seconds

    def server_startup(self):

        server_refresh = self.countdown_timer_server_refresh(5000)
        keys_generated = self.rsa_keyGen()

        if not keys_generated:
            print("##### Server has failed to generate RSA keys, retrying... #####")

        while keys_generated and (time.time() < server_refresh):
            data, address = self.UDPserver.recvfrom(self.bufferSize)
            self.receive_message(data, address)

    #################################### HELPER FUNCTIONS FOR SERVER ###########################################
    ### A Keep alive protocol that ensures a client is still active ###
    # def _keep_alive(self):
    #    while True:
    #        time.sleep(50)
    #        UDPserver.sendto("Are you still there?".encode('ascii'), ('', localPort))

    # def _reset_UDP_server(self):
    #    UDPserver.close()
    #    self.__init__()
    #    main()

    ### Pickle will be used to transport the list of IPs to the forwarder ###
    # def package_constructor(self):
    # pickled_data = pickle.dumps(ip_addresses)
    ### Only the forwarder should receive the pickled data, and should never be shared with the client besides the
    # forwarder ip_address ###
    #    return 0  # pickled_data

    ##########################################################################################################


def signal_handler_SIGINT():
    print("CTRL+C has been detected, exiting cleanly.")
    exit(0)


def signal_handler_SIGABRT():
    print("Aborting the program")
    sys.exit(0)


def main():
    try:
        while True:
            main_Server = CentralServer()
            main_Server.server_startup()
            print("\n****** Server has been refreshed ******\n")


    ## ERROR: with Daemon threads still using stdin
    except KeyboardInterrupt:
        signal.signal(signal.SIGABRT, signal_handler_SIGABRT())
        # signal.raise_signal(signal.SIGKILL)
    # except signal.SIGINT:
    #    signal.signal(signal.SIGINT, signal_handler_SIGINT())


if __name__ == "__main__":
    print(os.name)
    main()
