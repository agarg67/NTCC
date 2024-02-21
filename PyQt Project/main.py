from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit, QLineEdit
from network_thread import NetworkThread

class ClientUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Client Control Panel')
        self.setGeometry(100, 100, 600, 400)  # x, y, width, height

        # Setup the UI components as before...
        # Central Widget and Layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Command Input, Send Button, Display Area...

        # Initialize the network thread
        self.network_thread = NetworkThread()
        # Connect the signal to the slot to update the display area
        self.network_thread.update_display_signal.connect(self.update_display)

        # Start the network thread
        self.network_thread.start()

    def send_command(self):
        # Get the command from the input field and send it
        command = self.command_input.text()
        self.network_thread.send_command(command)

    def update_display(self, message):
        # Slot to update the display area with messages from the network thread
        self.display_area.append(message)

if __name__ == '__main__':
    app = QApplication([])
    window = ClientUI()
    window.show()
    app.exec_()
