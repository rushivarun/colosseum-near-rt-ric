import sctp
import socket
from .ASN.helpers import decode_asn1_message

def sctp_receiver(host, port):
    # Create an SCTP socket
    sock = sctp.sctpsocket_tcp(socket.AF_INET)

    try:
        # Bind and listen for incoming connections
        sock.bind((host, port))
        sock.listen(5)
        print(f"Listening for incoming connections on {host}:{port}")

        while True:
            conn, addr = sock.accept()
            print(f"Connected to {addr}")

            # Receive a message
            received_data = conn.sctp_recv(1024)[0]

            # Decode the ASN.1 message
            decoded_message = decode_asn1_message(received_data)
            print(f"Received message: {decoded_message}")

            # Optionally, send a response or close the connection
            conn.close()

    finally:
        # Close the socket
        sock.close()
