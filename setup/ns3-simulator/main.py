import datetime
import pandas as pd
import csv
import sctp
import time
import socket
from ASN import helpers, mysqlconn
import json
# from . import mysqlconn


file_path = './dataset.csv'
now_time = datetime.datetime.now()
start_time = datetime.datetime(now_time.year, now_time.month, now_time.day, 10, 0, 0, 0)
filename = './output.csv'


# with open(filename, 'w', newline='') as csvfile:
#     # Determine the fieldnames from the first dictionary
    
#     fieldnames = data[0].keys()

#     # Create a writer object
#     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

#     # Write the header
#     writer.writeheader()

#     # Write the data rows
#     for row in data:
#         writer.writerow(row)

def send_logs_to_sctp(container_name, sctp_host, sctp_port):
    df = pd.read_csv(file_path)
    count = 0
    # Create SCTP socket
    
    # try:
    # while True:
        
        
    for column in df.columns:
        offset = 5*count
        timestamp = start_time + datetime.timedelta(minutes=offset)
        data = []
        # len_column = len((df[column]))
        inti_counter = 1
        for i in df[column]:
            # print(list(df[column]).index(i))
            # sock = sctp.sctpsocket_tcp(socket.AF_INET)
            # sock.connect((sctp_host, sctp_port))
            payload = {
                "sigtime": timestamp,
                "inti": inti_counter,
                "type": "signals",
                "signals": i,
                "offset": offset
            }
            # print(payload)
            data.append(payload)
            encoded_msg = helpers.encode_asn1_message("SimEnv", 1, str(payload), "", True)
            # sock.sctp_send(msg=encoded_msg)
            # sock.close() 
            inti_counter += 1
        mysqlconn.PushToSQL('localhost', 'signal_data', 'root', 'password', 'root_sig', data)
        count += 1
        # Get the latest logs from the container
        # time.sleep(10)
        
        # time.sleep(2)
        # sock.close() 
    # except Exception as e:
    #     print("Stopping log forwarding...", str(e))


if __name__ == "__main__":
    # Define your container name, SCTP host, and SCTP port here
    CONTAINER_NAME = "e2term"
    SCTP_HOST = "127.0.0.1"
    SCTP_PORT = 8000  # Replace with your SCTP port

    send_logs_to_sctp(CONTAINER_NAME, SCTP_HOST, SCTP_PORT)
    # data = mysqlconn.download_data
    # mysqlconn.active_handhelds(data)
