import socket
import select
import json
from datetime import datetime

def combined_server(host='0.0.0.0', port=80, log_file='server_log.txt'):
    """
    Starts a server that handles both TCP and UDP connections.
    Parameters:
    host (str): The hostname or IP address to bind the server to.
    port (int): The port number to bind the server to.
    log_file (str): The file where traffic logs will be saved.
    """
    
    # Create TCP socket
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((host, port))
    tcp_socket.listen(5)
    print(f"Server is listening on {host}:{port}...")

    # Create UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((host, port))

    # List of sockets to monitor
    sockets_list = [tcp_socket, udp_socket]

    while True:
        # Use select to wait for activity on any socket
        read_sockets, _, _ = select.select(sockets_list, [], [])

        for notified_socket in read_sockets:
            if notified_socket == tcp_socket:
                # Handle TCP connections
                connection, client_address = tcp_socket.accept()
                try:
                    data = connection.recv(4096)
                    if data:
                        # Log the traffic
                        log_traffic('TCP', client_address, data, log_file)
                        # Process the request
                        result = process_request(data)
                        response = json.dumps(result).encode('utf-8')
                        connection.sendall(response)
                except Exception as e:
                    print(f"TCP error: {e}")
                finally:
                    connection.close()
            elif notified_socket == udp_socket:
                # Handle UDP messages
                try:
                    data, address = udp_socket.recvfrom(4096)
                    if data:
                        # Log the traffic
                        log_traffic('UDP', address, data, log_file)
                        # Process the request
                        result = process_request(data)
                        response = json.dumps(result).encode('utf-8')
                        udp_socket.sendto(response, address)
                except Exception as e:
                    print(f"UDP error: {e}")

def log_traffic(protocol, address, data, log_file):
    """
    Logs the traffic data with a timestamp.
    Parameters:
    protocol (str): The protocol used (TCP or UDP).
    address (tuple): The address of the client.
    data (bytes): The data received from the client.
    log_file (str): The file where the log will be saved.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"{timestamp} {protocol} from {address}: {data.decode('utf-8')}\n"
    
    with open(log_file, 'a') as file:
        file.write(log_entry)
    
    print(log_entry.strip())

def detect_attack(log_file):
    """
    Detects potential attacks by analyzing the log file.
    Parameters:
    log_file (str): The file where the log is saved.
    """
    with open(log_file, 'r') as file:
        lines = file.readlines()
        
    attack_ips = set()
    attack_methods = {
        'DDoS': [],
        'Phishing': [],
        'Malware': [],
        'Unauthorized Access': []
        # Add more attack methods as necessary
    }
    
    for line in lines:
        if "attack detected" in line:
            parts = line.split(' ')
            ip = parts[-1].strip()  # Assuming the IP is at the end of the line
            method = identify_attack_method(line)
            attack_ips.add(ip)
            if method in attack_methods:
                attack_methods[method].append(ip)
    
    for ip in attack_ips:
        print(f"Possible attack from IP: {ip}")
        
    for method, ips in attack_methods.items():
        print(f"\n{method} Attacks:")
        for ip in ips:
            print(f" - {ip}")

def identify_attack_method(log_entry):
    """
    Identifies the type of attack based on the log entry.
    Parameters:
    log_entry (str): A single line from the log file.
    Returns:
    str: The type of attack detected.
    """
    if "DDoS" in log_entry:
        return 'DDoS'
    elif "Phishing" in log_entry:
        return 'Phishing'
    elif "Malware" in log_entry:
        return 'Malware'
    elif "Unauthorized access" in log_entry:
        return 'Unauthorized Access'
    else:
        return 'Unknown'

def process_request(data):
    """
    Processes the incoming request data.
    Parameters:
    data (bytes): The data received from the client.
    Returns:
    dict: A dictionary with a message indicating successful processing.
    """
    # Example function to process incoming data
    return {"message": "Request processed successfully"}

if __name__ == "__main__":
    combined_server()
    detect_attack('server_log.txt')