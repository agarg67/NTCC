Central Server (sending messages):
 ````
 The format of the messages that the server can receive is as follows:
 - ackcon <Public Key>: received initial request to connect from client and servers public key
 - ackquestion: received question from client
 - ackanswer: received answer from client
 - defaultclientcheck: checks if there is a client on the opposite side of the communication
 * - comrequest: received request to start communication
 - sendcomreq <public key> <(ip1 port1) (ip2 port2) ...>: send public key and a list of ip addresses to the client 
 - sendipmapper <object of ipmap>: send ip addresses to the forwarder and noise generator
 - receivedis: received request to disconnect from client

* This would be redundant and unnecessary to send to the client as it will be determined by the active clients

 ````

Client (sending messages):
````
* - reqcon: used to start initial connection between client and central server. If successful, the client sends its public key and ip address
- sendpubip <public key> <ip address>: used to send the public key and ip address to the central server
- sendquestion <question id> <question> <answer>: Used to send the question to server to start intial communication
- answerquestion <question id> <answer>: answer a provided question
* - ackanswer <question id>: Accept question's answer
* - nakanswer <question id>: Reject question's answer
- disreq: request to disconnect from Central server
- comrequest: request comunication to start
* - acksendcomereq: accept the list of ip addresses and public key
- message <message id> <messsage>: sending a message to a user
- messageack <message id>: implicit ack sends
- terminatecom: terminate communication
- terminatecomack: accept to terminate communication

* The following have been marked redundant and would need further analysis.
````


Forwarder:
````
- centralconnect: shows central server the forwarder exists
- ackreceiveipmapper: receive ip addresses from the central server
- sendipmapper: send ip addresses of other servers to the noise generator
- ackclientmessage: receive new message from client
- forwardmessage: forward message to the noise generator
- ackforwardmessage <message id>: explicit ack sends for the message sent to the noise generator
````

Noise Generator:
````
- ackclientmessage: receive message from forwader
- ackreceiveipmapper: receive ip addresses from the forwarder server
- cloneforwardmessage: clones received forward message and sends it to other servers 
````

Note:
```
Local input for non message will need to have CMD#? at start to diffrentiate
```

