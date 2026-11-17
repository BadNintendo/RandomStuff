import socket

def StressTestClient(host='127.0.0.1', port=3000):
    def send_tcp(message):
        try:
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.connect((host, port))
            tcp_socket.sendall(message.encode('utf-8'))
            response = tcp_socket.recv(4096)
            print(f"TCP Response: {response.decode('utf-8')}")
            tcp_socket.close()
        except Exception as e:
            print(f"TCP stress error: {e}")

    def send_udp(message):
        try:
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.sendto(message.encode('utf-8'), (host, port))
            response, _ = udp_socket.recvfrom(4096)
            print(f"UDP Response: {response.decode('utf-8')}")
            udp_socket.close()
        except Exception as e:
            print(f"UDP stress error: {e}")

    # Simulate normal traffic
    send_tcp("Normal TCP traffic")
    send_udp("Normal UDP traffic")

    # Simulate attack traffic
    send_tcp("attack detected DDoS from 127.0.0.1")
    send_udp("attack detected Malware from 127.0.0.1")

if __name__ == "__main__":
    StressTestClient()