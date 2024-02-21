from PyQt5.QtCore import QThread, pyqtSignal
from client import Client

class NetworkThread(QThread):
    # Define signals for UI updates and error handling
    update_display_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, ip, port1, port2):
        super().__init__()
        # Initialize Client with IP and port details
        self.client = Client(ip, port1, port2)
        self.client.createSocket()  # Assuming this needs to be called to setup the client

    def run(self):
        # Implement if there's a specific loop for receiving messages
        # Placeholder for demonstration
        pass

    def send_command(self, command, *args):
        # Map commands to client methods
        try:
            if command == 'sendPublickeyIP':
                self.client.sendPublickeyIP()
            elif command == 'sendQuestionToServer':
                question, answer = args
                self.client.sendQuestionToServer(question, answer)
            elif command == 'sendMessage':
                message, = args
                self.client.sendMessage(message)
            elif command == 'answerQuestion':
                qid, answer = args
                self.client.answerQuestion(qid, answer)
            else:
                self.error_signal.emit(f"Unsupported command: {command}")
                return
            self.update_display_signal.emit(f"Command executed: {command} {args}")
        except Exception as e:
            self.error_signal.emit(f"Error executing command: {str(e)}")

    def connect_to_server(self):
        # Placeholder for server connection logic
        # You may need to use fetch_data_Central or fetch_data_relay here
        pass

    def parse_incoming_message(self, message):
        # Use client's parsing method for incoming messages
        try:
            parsed_message = self.client.parseIncomingMessage(message)
            self.update_display_signal.emit(parsed_message)
        except Exception as e:
            self.error_signal.emit(f"Error parsing message: {str(e)}")
