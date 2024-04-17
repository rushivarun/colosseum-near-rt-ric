import mysql.connector
from datetime import datetime, timedelta


def PushToSQL(host, database, user, password, table_name, data):
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