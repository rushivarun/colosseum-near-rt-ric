import sctp
import socket
from .ASN.helpers import encode_asn1_message

def sctp_sender(host, port, sender, criticality, signals, active):
    # Encode the message in ASN.1 format
    asn1_encoded_message = encode_asn1_message(sender, criticality, signals, active)

    # Create an SCTP socket
    sock = sctp.sctpsocket_tcp(socket.AF_INET)

    try:
        # Connect to the server
        sock.connect((host, port))

        # Send the ASN.1 encoded message
        sock.sctp_send(msg=asn1_encoded_message)

        print("ASN.1 message sent")
    finally:
        # Close the socket
        sock.close()


sctp_sender("10.0.2.1", "36422", "21", 2, [1, 3, 2], False)