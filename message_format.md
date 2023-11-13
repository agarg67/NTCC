Central Server:
 ````
 The format of the messages that the server can receive is as follows:
 - ackcon: received initial request to connect from client
 - ackpubip: received public key and ip address from client
 - ackquestion: received question from client
 - ackanswer: received answer from client
 - defaultclientcheck: checks if there is a client on the opposite side of the communication
 - ackcomreq: received request to start communication
 - sendcomreq: send public key and a list of ip addresses to the client 
 - sendipmapper: send ip addresses to the forwarder and noise generator
 ````


Client:

reqcon: used to start initial connection between client and central server. If successful, the client sends its public key and ip address

sendpubip <public key> <ip address >: used to send the public key and ip address to the central server

sendquestion <question id> <question>: Used to send the question to server to start intial communication

answerquestion <question id> <answer>: answer a provided question

ackanswer <question id>: Accept question's answer

initiatecomreq: request comunication to start

message <message id> <messsage>: sending a message to a user

messageack <message id>: implicit ack sends

terminatecom: terminate communication

terminatecomack: accept to terminate communication


Forwarder:


Noise Generator:


