import socket

def send(localPort, message):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', localPort))
    client.sendall(message.encode())
    client.shutdown(socket.SHUT_WR)

    response = client.recv(4096)
    print("recieved response from server")

    client.close()

if __name__ == "__main__":
    localPort = 8080
    messageToSend = "hi mijo"

    send(localPort, messageToSend)