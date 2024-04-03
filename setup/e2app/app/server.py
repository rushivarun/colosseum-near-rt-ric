import socket
import sctp

def sctp_sender(host, port, message):
    # Create an SCTP socket
    sock = sctp.sctpsocket_tcp(socket.AF_INET)

    try:
        # Connect to the server
        sock.connect((host, port))

        # Send a message
        sock.sctp_send(msg=message)

        print("Message sent")
    finally:
        # Close the socket
        sock.close()

# Run the server
run_server()

