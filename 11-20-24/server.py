import socket
import select
import json
import time
from ratelimit import limits, sleep_and_retry
from QRProcessor import QRPx2025  # Import the QRPx2025 class from the module

processed_requests = {}  # Storing the previous request
REQUEST_LIMIT = 500      # Define the rate limit (500 requests per minute)
TIME_PERIOD = 60         # 60 seconds
CACHE_SIZE_LIMIT = 1000  # Define cache size limit

qprx = QRPx2025(seed=12345)

@sleep_and_retry
@limits(calls=REQUEST_LIMIT, period=TIME_PERIOD)
def process_request(data):
    """
    Process the incoming request data.

    :param data: The data received in the request.
    :return: The processed result or error message.
    """
    try:
        request_data = json.loads(data.decode('utf-8'))
        cities = request_data['data']
        received_hash = request_data['hash']

        if received_hash in processed_requests:
            return processed_requests[received_hash]

        calculated_hash = qprx.custom_hash(json.dumps(cities).encode('utf-8').decode('utf-8'))
        if received_hash != calculated_hash:
            return {"error": "Hash verification failed"}

        result = qprx.dont_matter(cities)
        processed_requests[received_hash] = result

        if len(processed_requests) > CACHE_SIZE_LIMIT:
            processed_requests.pop(next(iter(processed_requests)))

        return result
    except Exception as e:
        return {"error": str(e)}

def combined_server(host='0.0.0.0', port=3000):
    """
    Start the combined TCP and UDP server.

    :param host: The host address for the server to bind to.
    :param port: The port number for the server to listen on.
    """
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((host, port))
    tcp_socket.listen(5)
    print(f"Server is listening on {host}:{port}...")

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((host, port))
    sockets_list = [tcp_socket, udp_socket]

    while True:
        read_sockets, _, _ = select.select(sockets_list, [], [])
        for notified_socket in read_sockets:
            if notified_socket == tcp_socket:
                connection, _ = tcp_socket.accept()
                try:
                    data = connection.recv(4096)
                    if data:
                        response = process_request(data)
                        connection.sendall(json.dumps(response).encode('utf-8'))
                except Exception as e:
                    print(f"TCP error: {e}")
                finally:
                    connection.close()
            elif notified_socket == udp_socket:
                try:
                    data, address = udp_socket.recvfrom(4096)
                    if data:
                        response = process_request(data)
                        udp_socket.sendto(json.dumps(response).encode('utf-8'), address)
                except Exception as e:
                    print(f"UDP error: {e}")

if __name__ == "__main__":
    combined_server()