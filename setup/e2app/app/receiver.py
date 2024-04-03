import sctp
import socket

def sctp_receiver(host, port):
    # Create an SCTP socket
    sock = sctp.sctpsocket_tcp(socket.AF_INET)

    try:
        # Bind the socket to an address and port
        sock.bind((host, port))

        # Listen for incoming connections
        sock.listen(5)
        print("Waiting for a connection...")

        # Accept a connection
        conn, addr = sock.accept()
        print(f"Connected to {addr}")

        # Receive a message
        message = conn.recv(1024)
        print(f"Received message: {message}")

    finally:
        # Close the socket
        sock.close()

# Example usage
sctp_receiver('127.0.0.1', 12345)