import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta

def download_data():
    # Connect to the MySQL database
    conn = mysql.connector.connect(
        host='localhost',       # Typically 'localhost' or an IP address
        user='root',   # Your MySQL username
        password='password',  # Your MySQL password
        database='signal_data'  # Your MySQL database name
    )
    cursor = conn.cursor()
    
    # Fetch all relevant data
    cursor.execute("SELECT sigtime, inti, signals FROM root_sig")
    data = cursor.fetchall()
    
    # Close the connection
    cursor.close()
    conn.close()
    
    return data

def get_active_handhelds(data, check_timestamp):
    # print(data)
    # Convert check_timestamp to a datetime object
    check_time = datetime.strptime(check_timestamp, "%Y-%m-%d %H:%M:%S")
    
    # Prepare to track signals over the relevant period
    time_frames = [check_time - timedelta(minutes=5 * i) for i in range(3)]
    signals_history = {time_frame: {} for time_frame in time_frames}
    inti_signals = {time_frame: {} for time_frame in time_frames}
    for entry in data:
        timestamp, handheld_id, signals = entry
        if timestamp in signals_history:
            signals_history[timestamp][handheld_id] = signals > 0  # True if signals were sent
            inti_signals[timestamp][handheld_id] = signals
    # print(inti_signals)
    # Determine active handhelds
    active_handhelds = []
    for handheld_id in signals_history[check_time - timedelta(minutes=10)]:
        if all(signals_history.get(time_frame, {}).get(handheld_id, False) for time_frame in time_frames):
            active_handhelds.append(handheld_id)

    signal_payload = transform_signals(inti_signals)
    print(active_handhelds)
    return active_handhelds, signal_payload

def transform_signals(signals_history):
    # Initialize the result list
    results = []

    # Extract and sort the timestamps
    sorted_times = sorted(signals_history.keys(), reverse=True)

    # Collect data for each handheld
    handheld_signals = {}
    for time in sorted_times:
        for handheld_id, signal in signals_history[time].items():
            if handheld_id not in handheld_signals:
                handheld_signals[handheld_id] = []
            handheld_signals[handheld_id].append(signal)
    
    # Format the results as required
    for handheld_id, signals in handheld_signals.items():
        results.append({handheld_id: signals})

    return results