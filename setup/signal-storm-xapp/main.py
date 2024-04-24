import socket
import json
import time
import numpy as np
from db import sqlconn
import datetime

def simulate_network_traffic(kpi_profiles, num_ta, hours=24, interval=5, anomaly_factor=5):
    """
    Simulate network traffic and detect anomalies.
    """
    num_intervals = (hours * 60) // interval
    anomaly_threshold = anomaly_factor  # Multiples of standard deviation
    anomalies = []

    for t in range(num_intervals):
        for i in range(num_ta):
            mu, sigma = kpi_profiles[i]
            # Normal traffic pattern
            observed_rsr = np.random.normal(mu[t], sigma[t])
            # Introduce anomalies at random
            if np.random.rand() < 0.1:  # 10% chance of anomaly
                observed_rsr += anomaly_threshold * sigma[t] * np.random.uniform(1, 3)
            # Compute anomaly score
            anomaly_score = abs(observed_rsr - mu[t]) / sigma[t]
            if anomaly_score > anomaly_threshold:
                anomalies.append((t, i, observed_rsr, anomaly_score))
    
    return anomalies

def detect_anomalies_remido(active_handhelds, threshold=3):
    data = sqlconn.query_database(active_handhelds)
    # print(data)
    """Function to detect anomalies in the dataset based on the given threshold."""
    anomalies = []
    # print(data)
    for record in data:
        # print(record)
        anomaly_score = (record['signals'] - record['ta_mean']) / record['ta_sd']
        if abs(anomaly_score) > threshold:
            print(anomaly_score)
            print(record["inti"])
            anomalies.append(record)
    return anomalies

def detect_anomalies(data):
    """
    Detects anomalies in a dataset of signal values from multiple handheld devices,
    where each handheld device's signal values are measured at regular time intervals.
    
    Args:
    data (dict): Dictionary where each key is a handheld ID and the value is a list of signals.
    
    Returns:
    dict: A dictionary with time intervals as keys and lists of tuples as values.
          Each tuple contains the handheld ID and the anomalous signal value for that interval.
    """
    # Initialize a list to hold signals for each time interval
    max_length = max(len(signals) for signals in data.values())  # Find the maximum list length
    interval_signals = [[] for _ in range(max_length)]  # Create lists for each interval

    # Aggregate signals by time interval across all handhelds
    for signals in data.values():
        for index, value in enumerate(signals):
            if index < max_length:
                interval_signals[index].append(value)

    # Dictionary to store anomalies
    anomalies = {i: [] for i in range(max_length)}

    # Calculate anomalies using statistical thresholds for each time interval
    for index, signals in enumerate(interval_signals):
        if len(signals) > 0:  # Ensure there are data points to analyze
            mean = np.mean(signals)
            std_dev = np.std(signals)
            threshold = mean + 3 * std_dev  # Dynamic threshold
            # Check each handheld's signal at this index against the threshold
            for handheld_id, handheld_signals in data.items():
                if index < len(handheld_signals) and handheld_signals[index] > threshold:
                    anomalies[index].append((handheld_id, handheld_signals[index]))

    return anomalies

def start_server(host='0.0.0.0', port=9000, window_size=3):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()

        print(f"Server started. Listening on {host}:{port}", flush=True)
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}", flush=True)
                data = conn.recv(1024).decode()
                if not data:
                    return
                input_data = json.loads(data)
                print(input_data)
                if input_data["type"] == "message":
                    response = json.dumps(input_data)
                    print(response, flush=True)
                    conn.sendall(response.encode())
                    
                else:
                    try:
                        input_data = input_data["metadata"]
                        data = sqlconn.download_data()
                        active_hh, signal_data = sqlconn.get_active_handhelds(data, "2024-04-17 10:50:00")
                        flattened_data = {k: v for d in signal_data for k, v in d.items()}
                        max_dev_series_id = detect_anomalies(flattened_data)
                        print(max_dev_series_id, flush=True)
                    except json.JSONDecodeError:
                        response = "Error decoding JSON"
                        print(response, flush=True)
                    conn.sendall(response.encode())

# Start the server
while True:
    # try:
    data = sqlconn.download_data()
    last_timestamp, _, _ = data[-1]
    active_hh, signal_data = sqlconn.get_active_handhelds(data, last_timestamp)
    active_data = [{
        "act_timestamp": last_timestamp,
        "active_handhelds": len(active_hh)
    }]
    sqlconn.PushToSQL(active_data)
    flattened_data = {k: v for d in signal_data for k, v in d.items()}
    max_dev_series_id = detect_anomalies(flattened_data)
    print("ANOMALY")
    remido_results = detect_anomalies_remido(active_hh)
    print(remido_results)
    logs_message = {
        "type": "XApp",
        "log_time": datetime.datetime.now(),
        "message": json.dumps({
            "anomalous": max_dev_series_id,
            "latest_timestamp": last_timestamp.isoformat()
        }),
        "origin": "XApp",
        "dest": "e2term"
    }
    sqlconn.PushToSQLLogs('localhost', 'signal_data', 'root', 'password', 'logs', [logs_message])
    print(max_dev_series_id, flush=True)
    sqlconn.insert_data_into_anomaly_detection(max_dev_series_id)
    time.sleep(2)
    # except Exception as e:
    #     print("Exception: {}".format(str(e)))
    #     time.sleep(10)
    #     continue
    


