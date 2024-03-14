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
        self.server_ips = []
    def __enter__(self):
        return self.server_ips

    def add_IP_addr(self, ip_addr):
        self.server_ips.append(ip_addr)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class CentralServer:

    def __init__(self):
        # Defining variables for the server:
        self.server_uptime = time.time()
        self.localPort = 20001
        self.bufferSize = 128000
        self.active_clients_and_keys = {}
        self.client_custom_names = {}
        self.received_messages = {}
        self.questions_and_answer = {}
        self.clients_com = {}
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

    def addtional_question_editor(self, data):
        additional_message = data.split(b" <")
        additional_message[3] = additional_message[3].replace(b">", b"")
        return additional_message[3]

    def addtional_answer_editor(self, data):
        additional_message = data.split(b" <")
        additional_message[4] = additional_message[4].replace(b">", b"")
        return additional_message[4]


    # NEED To add a function that splits the message into 245 byte chunks and encrypts them separately
    def split_and_encrypt(self, message, client_public_key):

        whole_encrypted_message = b""

        if (len(message) <= 245):
            whole_encrypted_message = rsa.encrypt(message, client_public_key)
        else:
            for i in range(0, len(message), 245):
                message_chunk = message[i:i + 245]
                whole_encrypted_message += rsa.encrypt(message_chunk, client_public_key)

        return whole_encrypted_message

    # NEED To add a function that decrypts the message and combines the 245 byte chunks
    def split_and_decrypt(self, message):

        decrypted_message = b""

        if (len(message) <= 256):
            decrypted_message = rsa.decrypt(message, self.rsaPrivateKey)
        else:
            for i in range(0, len(message), 256):
                message_chunk = message[i:i + 256]
                decrypted_message += rsa.decrypt(message_chunk, self.rsaPrivateKey)

        return decrypted_message

    ## Apparently only the sendpubip and forwarder messages will be unecrypted, everything else will be assumed encrypted ##

    ## TO DO : NEED TO ADD FLAGS IN ORDER FOR THE CLIENT TO FOLLOW THE PROTOCOLS ##


    def parse_message(self, data, addr):

        print("This is the data received: {}".format(data))

        # Default values for all messages received
        identifier_flag = None
        source_ip = addr[0].encode()
        pem = self.rsaPublicKey.save_pkcs1()
        server_ip = self.fetch_ip_address().encode()
        initiate_communication = False
        other_client = None

        print(self.clients_com)

        #if not self.clients_com:
        #    other_client = self.clients_com[addr][0]
        #    initiate_communication = True

        if (b"sendpubip" in data) or (b"forwarder" in data):
            identifier_flag = self.message_identifier(data)
            message_content = self.main_message(data)
            message_sender = self.message_sender(data)

        if identifier_flag == b"sendpubip":

            client_public_key = rsa.PublicKey.load_pkcs1(message_content.decode())

            # Need the address to be in bytes in order to be compared with the message_sender
            if source_ip == message_sender:

                if addr not in self.active_clients_and_keys:

                    self.active_clients_and_keys.setdefault(addr, client_public_key)
                    message = (b"ackcon <" + pem + b"> <" + server_ip + b">")

                    encrypted_message = self.split_and_encrypt(message, client_public_key)

                    self.UDPserver.sendto(encrypted_message, addr)

                    time.sleep(0.5)

                    # Proceeds then to ask the custom name for the client
                    message = (b"unameCS <" + str(addr).encode() + b"> <" + server_ip + b">")
                    encrypted_message = self.split_and_encrypt(message, client_public_key)
                    self.UDPserver.sendto(encrypted_message, addr)

                # Updates a client's public key if the client is already in the dictionary
                elif addr in self.active_clients_and_keys:
                    self.active_clients_and_keys[addr] = client_public_key
                    message = (b"ackcon <" + pem + b"> <" + server_ip + b">")

                    encrypted_message = self.split_and_encrypt(message, client_public_key)

                    self.UDPserver.sendto(encrypted_message, addr)

                    time.sleep(0.5)

                    # Proceeds then to ask the custom name for the client
                    message = (b"unameCS <" + str(addr).encode() + b"> <" + server_ip + b">")
                    encrypted_message = self.split_and_encrypt(message, client_public_key)
                    self.UDPserver.sendto(encrypted_message, addr)
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

                            # temp = json.dumps(server_ips).encode('utf-8')
                            # print(temp)

                            temp = json.dumps(ip_map.server_ips).encode('utf-8')
                            print(temp)

                            message = (b"ackipmapper <" + temp + b"> <" + server_ip + b">")
                            print(message)

                            encrypted_message = self.split_and_encrypt(message, self.forwarderPublicKey)
                            # encrypted_message = rsa.encrypt(message, self.forwarderPublicKey)
                            print(encrypted_message)

                            self.UDPserver.sendto(encrypted_message, addr)
                        else:
                            print("Forwarder has sent an incorrect key phrase or IP address")

            elif addr in self.active_clients_and_keys:

                if not self.active_clients_and_keys[addr]:
                    print("Client {} has not sent their public key".format(addr))
                else:

                    ciphertext = data
                    decrypted_message = self.split_and_decrypt(ciphertext)

                    identifier_flag = self.message_identifier(decrypted_message)
                    message_content = self.main_message(decrypted_message)
                    message_sender = self.message_sender(decrypted_message)

                    if identifier_flag == b"sendquestion":

                        question = None
                        answer = None

                        if (message_sender == source_ip) and (addr in self.active_clients_and_keys):

                            ack_question = False
                            question = self.addtional_question_editor(decrypted_message)
                            answer = self.addtional_answer_editor(decrypted_message)

                            if not self.questions_and_answer:
                                self.questions_and_answer.setdefault(addr, [question, answer, message_content])
                                ack_question = True

                            elif addr not in self.questions_and_answer:
                                self.questions_and_answer.setdefault(addr, [question, answer, message_content])
                                ack_question = True

                            elif addr in self.questions_and_answer:
                                self.questions_and_answer[addr] = [question, answer, message_content]
                                ack_question = True
                            else:
                                print("Error with adding the question and answer to the dictionary.")

                            if ack_question:
                                print(b"THIS IS THE QUESTION RECEIVED:" + question)
                                print(b"THIS IS THE ANSWER RECEIVED:" + answer)

                                message = (b"ackquestion" + b" <" + message_content + b"> <"
                                           + str(self.fetch_ip_address()).encode() + b">")

                                print(message)
                                encrypted_message = self.split_and_encrypt(message, self.active_clients_and_keys[addr])
                                print(encrypted_message)
                                self.UDPserver.sendto(encrypted_message, addr)
                        else:
                            print("Failed: Client {} is not in the active clients list".format(addr))





                    elif identifier_flag == b"sendnameserver":

                        if (addr in self.active_clients_and_keys) and (message_sender == source_ip):

                            print("Client {} has sent their custom name: {}".format(message_sender, message_content))
                            if not self.client_custom_names:
                                self.client_custom_names.setdefault(addr, message_content)
                            elif message_sender not in self.client_custom_names:
                                self.client_custom_names.setdefault(addr, message_content)
                            elif message_sender in self.client_custom_names:
                                self.client_custom_names[addr] = message_content
                            else:
                                print("Error: Custom name not added to the dictionary")

                            print(self.client_custom_names)

                    elif identifier_flag == b"comrequest":

                        if message_content == b"client_server":

                            # Purely for testing purposes
                            #self.client_custom_names.setdefault(('123.123.123.123', 29314), b"CRA##Z")
                            #self.questions_and_answer.setdefault(('123.123.123.123', 29314), [b"Question", b"Answer"])

                            if (len(self.client_custom_names.keys()) < 2) and (source_ip == message_sender):
                                print("There is only one client to communicate")

                                message = (b"comrequest <" + b"NO OTHER CLIENTS" + b"> <" + server_ip + b">")
                                encrypted_message = self.split_and_encrypt(message, self.active_clients_and_keys[addr])
                                self.UDPserver.sendto(encrypted_message, addr)

                            else:
                                print(
                                    "Client has requested to communicate with another client. Fetching active clients list:")

                                listofnames = []

                                for key in self.client_custom_names.keys():

                                    if key != addr:
                                        if isinstance(self.client_custom_names[key], bytes):
                                            client_name = self.client_custom_names[key].decode('utf-8')
                                            listofnames.append(client_name)

                                print(listofnames)

                                temp = json.dumps(listofnames).encode('utf-8')

                                print(temp)
                                message = (b"comrequest <" + temp + b"> <" + server_ip + b">")

                                print(message)

                                encrypted_message = self.split_and_encrypt(message, self.active_clients_and_keys[addr])
                                self.UDPserver.sendto(encrypted_message, addr)


                    elif identifier_flag == b"sendpartnerserver":

                        if (message_sender == source_ip):

                            print(message_content)

                            if (message_content in self.client_custom_names.values()):

                                print("Client {} has sent the partner server IP: {}".format(message_sender,
                                                                                            message_content))

                                # Purely for testing purposes
                                # self.client_custom_names.setdefault(('123.123.123.123', 29314), b"CRA##Z")

                                temp_key = None

                                print(self.client_custom_names.keys())

                                for key in self.client_custom_names.keys():
                                    if self.client_custom_names[key] == message_content:
                                        temp_key = key

                                if temp_key is not None:
                                    message = (b"sendquestion <" + self.questions_and_answer[temp_key][2] + b"> <" +
                                        self.questions_and_answer[temp_key][0] + b"> <" + server_ip + b">")

                                    message2 = (b"sendquestion <" + self.questions_and_answer[addr][2] + b"> <" +
                                               self.questions_and_answer[addr][0] + b"> <" + server_ip + b">")

                                    self.clients_com.setdefault(addr, [temp_key, False])
                                    self.clients_com.setdefault(temp_key, [addr, False])

                                    encrypted_message = self.split_and_encrypt(message, self.active_clients_and_keys[addr])
                                    encrypted_message2 = self.split_and_encrypt(message2, self.active_clients_and_keys[temp_key])

                                    self.UDPserver.sendto(encrypted_message, addr)
                                    self.UDPserver.sendto(encrypted_message2, temp_key)


                    elif identifier_flag == b"answerquestion":

                        if (addr in self.active_clients_and_keys) and (message_sender == source_ip):

                            print(identifier_flag)
                            print(message_content)

                            required_answer = self.questions_and_answer[self.clients_com[addr][0]][1]
                            print(required_answer)

                            if (message_content == self.questions_and_answer[self.clients_com[addr][0]][1]):
                                print("Client {} has answered the question correctly".format(message_sender))
                                self.clients_com[addr][1] = True

                                message = (b"ackanswer <" + b"Correct" + b"> <" + server_ip + b">")

                                encrypted_message = self.split_and_encrypt(message, self.active_clients_and_keys[addr])
                                self.UDPserver.sendto(encrypted_message, addr)
                            else:
                                message = (b"nakanswer <" + b"Correct" + b"> <" + server_ip + b">")

                                encrypted_message = self.split_and_encrypt(message, self.active_clients_and_keys[addr])
                                self.UDPserver.sendto(encrypted_message, addr)

                    elif initiate_communication and (self.clients_com[addr][1] and
                                                     self.clients_com[self.clients_com[other_client][1]]):

                        ip_map = ipMapper_manager()
                        ip_map.add_IP_addr(addr)
                        ip_map.add_IP_addr(other_client)

                        print("Both clients have answered the question correctly, initiating communication")

                        first_client_pub_key = self.active_clients_and_keys[addr].save_pkcs1()
                        second_client_pub_key = self.active_clients_and_keys[other_client].save_pkcs1()

                        message = (b"cominitiate" + b"<" + first_client_pub_key + b"> <" + server_ip + b">")
                        message2 = (b"cominitiate" + b"<" + second_client_pub_key + b"> <" + server_ip + b">")

                        encrypted_message = self.split_and_encrypt(message, self.forwarderPublicKey)
                        encrypted_message2 = self.split_and_encrypt(message2, self.forwarderPublicKey)

                        self.UDPserver.sendto(encrypted_message2, addr)
                        self.UDPserver.sendto(encrypted_message, other_client)

                        #message = (b"sendip")





                    else:
                        print("Message not recognized")
                        return None















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
            # print("Message not recognized")
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
