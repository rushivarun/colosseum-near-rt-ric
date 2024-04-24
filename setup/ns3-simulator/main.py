import datetime
import pandas as pd
import utils
import time
import random
from ASN import helpers, mysqlconn
# from . import mysqlconn


file_path = './ns3-simulator/data2.csv'
now_time = datetime.datetime.now()
start_time = now_time
filename = './ns3-simulator/output.csv'
BLACKLIST = True

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
    ta = {}
    while True:
        
        for column in df.columns:
            blacklisted_intis = mysqlconn.query_anomalous_data()
            # print(blacklisted_intis)
            offset = 5*count
            
            timestamp = start_time + datetime.timedelta(minutes=offset)
            data = []
            original_data = []
            logs = []
            inti_counter = 1

            for i in df[column]:
                if inti_counter not in ta.keys():
                    # print(inti_counter)
                    ta[inti_counter] = {
                        "ta": round(random.uniform(1, 10), 5),
                        "sd": round(random.uniform(0, 1), 5)
                    }
                if BLACKLIST:
                    if inti_counter in blacklisted_intis:
                        payload = {
                            "sigtime": timestamp,
                            "inti": inti_counter,
                            "type": "signals",
                            "signals": 0,
                            "offset": offset,
                            "ta_mean": ta[inti_counter]["ta"],
                            "ta_sd": ta[inti_counter]["sd"]
                        }
                        payload_real = {
                            "sigtime": timestamp,
                            "inti": inti_counter,
                            "type": "signals",
                            "signals": i,
                            "offset": offset,
                            "ta_mean": ta[inti_counter]["ta"],
                            "ta_sd": ta[inti_counter]["sd"]
                        }
                    else:
                        payload = {
                        "sigtime": timestamp,
                        "inti": inti_counter,
                        "type": "signals",
                        "signals": i,
                        "offset": offset,
                        "ta_mean": ta[inti_counter]["ta"],
                        "ta_sd": ta[inti_counter]["sd"]
                    }
                        payload_real = {
                        "sigtime": timestamp,
                        "inti": inti_counter,
                        "type": "signals",
                        "signals": i,
                        "offset": offset,
                        "ta_mean": ta[inti_counter]["ta"],
                        "ta_sd": ta[inti_counter]["sd"]
                    }
                else:
                    payload = {
                        "sigtime": timestamp,
                        "inti": inti_counter,
                        "type": "signals",
                        "signals": i,
                        "offset": offset,
                        "ta_mean": ta[inti_counter]["ta"],
                        "ta_sd": ta[inti_counter]["sd"]
                    }
                    payload_real = {
                        "sigtime": timestamp,
                        "inti": inti_counter,
                        "type": "signals",
                        "signals": i,
                        "offset": offset,
                        "ta_mean": ta[inti_counter]["ta"],
                        "ta_sd": ta[inti_counter]["sd"]
                    }                    
                # print(payload)
                data.append(payload)
                original_data.append(payload_real)
                encoded_msg, logs_message = helpers.encode_asn1_message("SimEnv", 1, str(payload), "", True)
                logs.append(logs_message)
                # sock.sctp_send(msg=encoded_msg)
                # sock.close()
                inti_counter += 1
            mysqlconn.PushToSQL('localhost', 'signal_data', 'root', 'password', 'logs', logs)
            mysqlconn.PushToSQL('localhost', 'signal_data', 'root', 'password', 'root_sig', data)
            mysqlconn.PushToSQL('localhost', 'signal_data', 'root', 'password', 'root_sig_org', original_data)
            count += 1
            # Get the latest logs from the container
            time.sleep(4)
            
        time.sleep(2)
    # except Exception as e:
    #     print("Stopping log forwarding...", str(e))


if __name__ == "__main__":
    mysqlconn.PushToSQL('localhost', 'signal_data', 'root', 'password', 'logs', [utils.Greeting()])
    # Define your container name, SCTP host, and SCTP port here
    CONTAINER_NAME = "e2term"
    SCTP_HOST = "127.0.0.1"
    SCTP_PORT = 8000  # Replace with your SCTP port
    # starting simulation
    mysqlconn.PushToSQL('localhost', 'signal_data', 'root', 'password', 'logs', [utils.IPSetup(SCTP_HOST, SCTP_PORT)])
    send_logs_to_sctp(CONTAINER_NAME, SCTP_HOST, SCTP_PORT)
