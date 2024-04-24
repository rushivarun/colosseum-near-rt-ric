import docker
import sctp
import time
import socket
from ASN import helpers
from db import database

def send_logs_to_sctp(container_name, sctp_host, sctp_port):
    # Initialize Docker client
    client = docker.from_env()

    # Get the specified container
    container = client.containers.get(container_name)

    # Create SCTP socket
    

    try:
        while True:
            # sock = sctp.sctpsocket_tcp(socket.AF_INET)
            # sock.connect((sctp_host, sctp_port))
            # Get the latest logs from the container
            logs = container.logs(tail=5)  # Gets the last 10 lines; adjust as needed
            encoded_msg, logs_message = helpers.encode_asn1_message("E2Term", 1, str(logs), "", True)
            database.PushToSQL('localhost', 'signal_data', 'root', 'password', 'logs', [logs_message])
            # Send the logs to the SCTP host and port
            # sock.sctp_send(msg=encoded_msg)
            # # Wait for 2 seconds
            time.sleep(2)
            # sock.close()
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
