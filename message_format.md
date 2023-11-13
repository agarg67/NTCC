Central Server:
 ````
 The format of the messages that the server can receive is as follows:
 - 
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


