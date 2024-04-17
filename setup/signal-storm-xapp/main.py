import socket
import json
import numpy as np
from db import sqlconn

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
                        flattened_data = {k: v for d in input_data for k, v in d.items()}
                        max_dev_series_id = series_with_max_deviation(flattened_data, window_size)
                        response = f"Series with the maximum deviation: {max_dev_series_id}"
                        print(response, flush=True)
                    except json.JSONDecodeError:
                        response = "Error decoding JSON"
                        print(response, flush=True)
                    conn.sendall(response.encode())

# Start the server
data = sqlconn.download_data()
active_hh, signal_data = sqlconn.get_active_handhelds(data, "2024-04-17 10:50:00")
flattened_data = {k: v for d in signal_data for k, v in d.items()}
max_dev_series_id = detect_anomalies(flattened_data)
print(max_dev_series_id, flush=True)
