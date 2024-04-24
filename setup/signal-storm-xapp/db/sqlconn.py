import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta

def download_data():
    try:
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
    except Exception as e:
        raise Exception(e)
    
    return data

def get_active_handhelds(data, check_timestamp):
    # print(data)
    # Convert check_timestamp to a datetime object
    # check_time = datetime.strptime(check_timestamp, "%Y-%m-%d %H:%M:%S")
    check_time = check_timestamp
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


def PushToSQL(data):
    conn = mysql.connector.connect(
        host='localhost',       # Typically 'localhost' or an IP address
        user='root',   # Your MySQL username
        password='password',  # Your MySQL password
        database='signal_data'  # Your MySQL database name
    )
    """
    Insert an array of dictionaries into a MySQL table.

    :param host: Hostname of the MySQL server
    :param database: Name of the database
    :param user: Username for the database
    :param password: Password for the database
    :param table_name: Name of the table where data will be inserted
    :param data: Array of dictionaries containing the data to be inserted
    """

    if conn.is_connected():
        cursor = conn.cursor()

        # Creating a placeholder for insertion
        placeholders = ', '.join(['%s'] * len(data[0]))
        columns = ', '.join(data[0].keys())
        sql = f"""
        INSERT INTO active_handhelds ({columns})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE
        """
        update_clause = ', '.join([f"{column}=VALUES({column})" for column in data[0].keys()])
        sql += update_clause  # Append the update clause to the SQL query

        # Preparing data for insertion
        insert_data = [tuple(item.values()) for item in data]

        # Executing the SQL command
        cursor.executemany(sql, insert_data)
        conn.commit()

        print("active handleds updated".format(len(data)))

def insert_data_into_anomaly_detection(sig_data):
    if not sig_data.get(2):
        return True
    data = []
    for inti, _ in sig_data[2]:
        data.append((inti, 1, 0))

    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(
            host='localhost',       # Typically 'localhost' or an IP address
            user='root',   # Your MySQL username
            password='password',  # Your MySQL password
            database='signal_data'  # Your MySQL database name
        )
        
        if conn.is_connected():
            cursor = conn.cursor()
            # SQL query for inserting data
            query = """
            INSERT INTO anomaly_detection (inti, anomalous, action_taken)
            VALUES (%s, %s, %s);
            """
            # Executing the SQL command for multiple records
            cursor.executemany(query, data)
            # Commit the changes to the database
            conn.commit()
            print(f"{cursor.rowcount} records inserted successfully.")
    except Error as e:
        print("Error while connecting to MySQL or inserting data", e)
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection is closed")


def PushToSQLLogs(host, database, user, password, table_name, data):
    """
    Insert an array of dictionaries into a MySQL table.

    :param host: Hostname of the MySQL server
    :param database: Name of the database
    :param user: Username for the database
    :param password: Password for the database
    :param table_name: Name of the table where data will be inserted
    :param data: Array of dictionaries containing the data to be inserted
    """
    # try:
        # Establishing the connection
    conn = mysql.connector.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )
    if conn.is_connected():
        cursor = conn.cursor()

        # Creating a placeholder for insertion
        placeholders = ', '.join(['%s'] * len(data[0]))
        columns = ', '.join(data[0].keys())
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        # Preparing data for insertion
        insert_data = [tuple(item.values()) for item in data]

        # Executing the SQL command
        cursor.executemany(sql, insert_data)
        conn.commit()

        print("dbaas service updated. Pushed {} records to message bus".format(len(data)))

def create_query(table_name, handheld_ids):
    """Function to create a SQL query for specific handheld IDs."""
    ids_string = ', '.join([str(id) for id in handheld_ids])
    query = f"SELECT * FROM {table_name} WHERE inti IN ({ids_string})"
    return query

def query_database(active_handhelds):
    query = create_query("root_sig", active_handhelds)
    try:
        connection = mysql.connector.connect(
            host='localhost',       # Typically 'localhost' or an IP address
            user='root',   # Your MySQL username
            password='password',  # Your MySQL password
            database='signal_data'  # Your MySQL database name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    """Function to execute a query and return the results."""
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")
    finally:
        cursor.close()
        connection.close()
    