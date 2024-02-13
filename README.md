# NTCC
CSE486 Capstone



## TESTING RESULTS
    ** Test #1 **
 Tested the connection between one client on a separate machine and the server running on Raspberry Pi 4.
    - The client was successfully able to connect to the server
    - The client was also able to send commands which were successfully received and recognized by the server
    - The server was also able to ping back to the client who has initiated the connection

Issues: 
    - Some of the client's commands (Packets) seemed to be lost in the process of sending and receiving, so it required
    multiple attempts to send the same command to the server.
    - Sometimes the client would become unreachable (seemingly random) and it would result in the server crashing. 
