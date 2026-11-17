import socket
import select
import json
from ratelimit import limits, sleep_and_retry
import time


processed_requests = {} # storing the previous request
REQUEST_LIMIT = 500 # Define the rate limit (500 requests per minute)
TIME_PERIOD = 60 # 60 seconds
CACHE_SIZE_LIMIT = 1000  # Define cache size limit

class QPRx2025:
    """Quantum Processing Relay: Instantly query a result!"""
    def __init__(self, seed=None):
        self.CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        self.LCG_PARAMS = {
            'a': 1664525,
            'c': 1013904223,
            'm': 4294967296
        }
        self.seed = None
        self.entropy = None
        if seed is not None:
            self.seed = seed % 1000000
            self.entropy = self.mix_entropy(int(time.time() * 1000))

    def mix_entropy(self, value):
        return value ^ (value >> 32) ^ (value >> 16) ^ (value >> 8) ^ value

    def lcg(self, a=None, c=None, m=None):
        if self.seed is None or self.entropy is None:
            raise ValueError('Seed and entropy must be initialized to use LCG')
        if a is None: a = self.LCG_PARAMS['a']
        if c is None: c = self.LCG_PARAMS['c']
        if m is None: m = self.LCG_PARAMS['m']
        self.seed = (a * self.seed + c + self.entropy) % m
        self.entropy = self.mix_entropy(self.seed + int(time.time() * 1000))
        return self.seed

    def mersenne_twister(self):
        if self.seed is None:
            raise ValueError('Seed must be initialized to use Mersenne Twister')
        MT = [0] * 624
        index = 0

        def initialize(seed):
            MT[0] = seed
            for i in range(1, 624):
                MT[i] = (0x6c078965 * (MT[i - 1] ^ (MT[i - 1] >> 30)) + i) & 0xffffffff

        def generate_numbers():
            for i in range(624):
                y = (MT[i] & 0x80000000) + (MT[(i + 1) % 624] & 0x7fffffff)
                MT[i] = MT[(i + 397) % 624] ^ (y >> 1)
                if y % 2 != 0:
                    MT[i] ^= 0x9908b0df

        def extract_number():
            nonlocal index
            if index == 0:
                generate_numbers()
            y = MT[index]
            y ^= y >> 11
            y ^= (y << 7) & 0x9d2c5680
            y ^= (y << 15) & 0xefc60000
            y ^= y >> 18
            index = (index + 1) % 624
            return y

        initialize(self.seed)
        return extract_number()

    def quantum_polls_relay(self, max_val):
        if not isinstance(max_val, int) or max_val <= 0:
            raise ValueError('Invalid max value for QuantumPollsRelay')
        lcg_value = self.lcg()
        mt_value = self.mersenne_twister()
        return ((lcg_value + mt_value) % 1000000) % max_val

    def generate_characters(self, length):
        if not isinstance(length, int) or length <= 0:
            raise ValueError('Invalid length for generateCharacters')
        return ''.join(self.CHARACTERS[self.quantum_polls_relay(len(self.CHARACTERS))] for _ in range(length))

    def alphabetical_order(self, index):
        """Generate alphabetical sequence based on index."""
        result = ''
        while index >= 0:
            result = chr(97 + index % 26) + result
            index = index // 26 - 1
        return result

    def morton_order(self, city):
        # Function to compute Morton order (Z-order curve) for sorting cities
        def interleave_bits(x, y):
            # Spread bits to interleave x and y coordinates
            def spread_bits(v):
                v = (v | (v << 8)) & 0x00FF00FF
                v = (v | (v << 4)) & 0x0F0F0F0F
                v = (v | (v << 2)) & 0x33333333
                v = (v | (v << 1)) & 0x55555555
                return v
            # Return interleaved bits of x and y
            return spread_bits(x) | (spread_bits(y) << 1)
        # Convert city coordinates to integers and scale them
        x = int(city['x'] * 10000)
        y = int(city['y'] * 10000)
        # Return the Morton order of the city
        return interleave_bits(x, y)
    
    def the_options(self, options):
        if not isinstance(options, list) or len(options) == 0:
            raise ValueError('No options provided')
        return options[self.quantum_polls_relay(len(options))]

    def the_rewarded(self, participants):
        if not isinstance(participants, list) or len(participants) == 0:
            raise ValueError('No participants provided')
        return participants[self.quantum_polls_relay(len(participants))]

    def generate_uuid(self):
        bytes_array = [self.mersenne_twister() + self.quantum_polls_relay(256) & 0xff for _ in range(16)]
        bytes_array[6] = (bytes_array[6] & 0x0f) | 0x40
        bytes_array[8] = (bytes_array[8] & 0x3f) | 0x80
        uuid = ''.join(f'{b:02x}' for b in bytes_array)
        return f'{uuid[:8]}-{uuid[8:12]}-{uuid[12:16]}-{uuid[16:20]}-{uuid[20:]}'

    def custom_hash(self, input, salt='', hash_val=False):
        def hashing(input, salt):
            combined = f'{input}{salt}'
            hashed = 0x811c9dc5
            for char in combined:
                hashed ^= ord(char)
                hashed = (hashed * 0x01000193) & 0xffffffff
            return f'{hashed:08x}'

        def verify_hash(input, salt, hashed):
            return hashing(input, salt) == hashed

        if isinstance(hash_val, str):
            return verify_hash(input, salt, hash_val)
        return hashing(input, salt)

    def xor_cipher(self, input, key):
        return ''.join(chr(ord(input[i]) ^ ord(key[i % len(key)])) for i in range(len(input)))

    def dont_matter(self, cities):
        """Sort and connect cities based on the least x and y values."""
        if not cities:
            print("No cities to process. Please check the input data.")
            return []

        # Record start time for initial sorting
        start_sort_time = time.time()
        
        # Sort cities based on Morton order for initial sorting
        cities_sorted = sorted(cities, key=self.morton_order)
        sorted_path = []
        current_city = cities_sorted[0]
        sorted_path.append(current_city)

        while cities_sorted:
            cities_sorted.remove(current_city)
            if not cities_sorted:
                break
            # Find the closest city in the sorted list
            closest_city = min(cities_sorted, key=lambda city: (city['x'], city['y']))
            sorted_path.append(closest_city)
            current_city = closest_city
        
        # Ensure the first city is also placed at the end to form a loop
        if sorted_path:
            sorted_path.append(sorted_path[0])

        # Record end time for sorting
        end_sort_time = time.time()
        sort_time = round((end_sort_time - start_sort_time) * 1000, 2)  # Convert to milliseconds

        print(f"Sort Time (ms): {sort_time}")

        return sorted_path

# Initialize QPRx2025
qprx = QPRx2025(seed=12345)

# Rate limiting decorator
@sleep_and_retry
@limits(calls=REQUEST_LIMIT, period=TIME_PERIOD)
def process_request(data):
    try:
        request_data = json.loads(data.decode('utf-8'))
        cities = request_data['data']
        received_hash = request_data['hash']

        # Check if the hash already exists in the processed_requests
        if received_hash in processed_requests:
            return processed_requests[received_hash]

        # Calculate the hash of the cities data
        calculated_hash = qprx.custom_hash(json.dumps(cities).encode('utf-8').decode('utf-8'))

        # Verify the hash
        if received_hash != calculated_hash:
            return {"error": "Hash verification failed"}

        # Process the data
        result = qprx.dont_matter(cities)
        processed_requests[received_hash] = result

        # Check cache size and clear if necessary
        if len(processed_requests) > CACHE_SIZE_LIMIT:
            processed_requests.pop(next(iter(processed_requests)))

        return result
    except Exception as e:
        return {"error": str(e)}

def combined_server(host='0.0.0.0', port=3000):
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
                        result = process_request(data)
                        response = json.dumps(result).encode('utf-8')
                        udp_socket.sendto(response, address)
                except Exception as e:
                    print(f"UDP error: {e}")

if __name__ == "__main__":
    combined_server()