from client import Client
import random

def test_client():

    client = Client("localhost", 0, 0)

    try:
        client.createSocket()
        
        print("If you don't see a message that says 'failed to find available port', the socket was created successfully.")
        
        # Test connection setup methods
        print("Testing sendPublickeyIP...")
        client.sendPublickeyIP()

        # Ensure arguments are adjusted according to the method definition in Client
        print("Testing sendQuestionToServer...")
        client.sendQuestionToServer("This is a test question", "Test answer")

        print("Testing sendMessage...")
        client.sendMessage("This is a test message.")

        print("Testing answerQuestion...")
        client.answerQuestion("test_question_id", "Test answer")

    except Exception as e:
        print(f"An error occurred during testing: {e}")
    finally:
        # Ensure sockets are closed even if an error occurs
        print("Closing sockets...")
        client.closeSockets()

if __name__ == "__main__":
    test_client()
