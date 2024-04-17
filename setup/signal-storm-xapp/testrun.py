import socket
import json

def send_data_to_server(host, port, data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        
        # Convert data to JSON string and send it
        json_data = json.dumps(data)
        s.sendall(json_data.encode())

        # Receive the response from the server and print it
        response = s.recv(1024)
        print(response.decode())

if __name__ == "__main__":
    host = 'localhost'  # The server's hostname or IP address
    port = 9000         # The port used by the server

    input_data = [
        {1: [0, 12, 34, 21, 43, 21, 12]}, 
        {2: [0, 12, 34, 21, 43, 21, 12]}, 
        {3: [90, 12, 34, 71, 43, 46, 12]}
    ]

    # input_data = [
    #     {"message": "x_app connected to E2 Temrination on 10.9.0.2"}
    # ]
    op = {
        "type": "message",
        "metadata": input_data
    }

    send_data_to_server(host, port, op)
