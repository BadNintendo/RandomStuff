import socket
import json

# Connect to AntPool
host = "stratum.antpool.com"
port = 3333
sock = socket.create_connection((host, port))

# Subscribe to Stratum
subscribe_msg = json.dumps({
    "id": 1,
    "method": "mining.subscribe",
    "params": []
}) + "\n"
sock.sendall(subscribe_msg.encode())

# Receive and parse response
response = sock.recv(1024).decode()
print("Response:", response)

# Authenticate (replace with your credentials)
auth_msg = json.dumps({
    "id": 2,
    "method": "mining.authorize",
    "params": ["BadNin", "x"]
}) + "\n"
sock.sendall(auth_msg.encode())

response = sock.recv(1024).decode()
print("Authentication Response:", response)