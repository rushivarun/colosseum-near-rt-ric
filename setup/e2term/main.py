import docker
import sctp
import time
import socket
from ASN import helpers

def send_logs_to_sctp(container_name, sctp_host, sctp_port):
    # Initialize Docker client
    client = docker.from_env()

    # Get the specified container
    container = client.containers.get(container_name)

    # Create SCTP socket
    

    try:
        while True:
            sock = sctp.sctpsocket_tcp(socket.AF_INET)
            sock.connect((sctp_host, sctp_port))
            # Get the latest logs from the container
            logs = container.logs(tail=5)  # Gets the last 10 lines; adjust as needed
            encoded_msg = helpers.encode_asn1_message("E2Term", 1, str(logs), "", True)
            # Send the logs to the SCTP host and port
            print(encoded_msg)
            sock.sctp_send(msg=encoded_msg)
            print("Sleeping")
            # # Wait for 2 seconds
            time.sleep(2)
            sock.close()
    except Exception as e:
        print("Stopping log forwarding...", str(e))
    # finally:
    #     sock.close()

if __name__ == "__main__":
    # Define your container name, SCTP host, and SCTP port here
    CONTAINER_NAME = "e2term"
    SCTP_HOST = "127.0.0.1"
    SCTP_PORT = 8000  # Replace with your SCTP port

    send_logs_to_sctp(CONTAINER_NAME, SCTP_HOST, SCTP_PORT)
