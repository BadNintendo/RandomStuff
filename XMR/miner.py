import socket
import json
import hashlib
import time
import threading

class QPRx2025:
    """Quantum Processing Relay: Instantly query a result!"""
    def __init__(self, seed=None):
        self.CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        self.LCG_PARAMS = {
            'a': 1664525,
            'c': 1013904223,
            'm': 4294967296
        }
        self.seed = seed % 1000000 if seed is not None else None
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

# Morton order and don't matter functions
def morton_order(city):
    def interleave_bits(x, y):
        def spread_bits(v):
            v = (v | (v << 8)) & 0x00FF00FF
            v = (v | (v << 4)) & 0x0F0F0F0F
            v = (v | (v << 2)) & 0x33333333
            v = (v | (v << 1)) & 0x55555555
            return v
        return spread_bits(x) | (spread_bits(y) << 1)
    x = int(city['x'] * 10000)
    y = int(city['y'] * 10000)
    return interleave_bits(x, y)

def dont_matter(cities):
    if not cities:
        print("No cities to process. Please check the input data.")
        return []
    cities_sorted = sorted(cities, key=morton_order)
    sorted_path = [cities_sorted.pop(0)]
    cities_sorted.sort(key=lambda city: (city['x'], city['y']))
    sorted_path.extend(cities_sorted)
    sorted_path.append(sorted_path[0])
    return sorted_path

class XMRMiner:
    def __init__(self, pool_url, miner_id):
        self.pool_url = pool_url.replace("stratum+tcp://", "")
        self.miner_id = miner_id
        self.socket = None
        self.job_id = None
        self.target = None
        self.qprx = QPRx2025(seed=12345)  # Initialize QPRx2025 with a seed

    def connect(self):
        host, port = self.pool_url.split(":")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, int(port)))
        print(f"Connected to pool {self.pool_url}")

    def send(self, data):
        try:
            message = json.dumps(data).encode('utf-8')
            self.socket.sendall(message)
            print(f"Sent: {data}")
        except Exception as e:
            print(f"Error sending data: {e}")

    def receive(self):
        try:
            response = self.socket.recv(1024)
            decoded_response = response.decode('utf-8').split("\n")
            print(f"Received: {decoded_response}")
            return [json.loads(line) for line in decoded_response if line]
        except Exception as e:
            print(f"Error receiving data: {e}")
            return []

    def subscribe(self):
        self.send({
            "method": "login",
            "params": {
                "login": self.miner_id,
                "pass": "x",
                "agent": "xmr-python-miner"
            },
            "id": 1
        })
        while True:
            responses = self.receive()
            for response in responses:
                print("Subscription response:", response)
                if 'result' in response and 'job' in response['result']:
                    self.job_id = response['result']['job']['job_id']
                    self.target = response['result']['job']['target']
                    self.job_blob = response['result']['job']['blob']
                    self.seed_hash = response['result']['job']['seed_hash']
                    print(f"Subscribed with job ID: {self.job_id}")
                    return response['result']['job']
                elif 'error' in response and response['error']:
                    print(f"Error subscribing: {response['error']}")
                    return None
            print("Retrying subscription in 5 seconds...")
            time.sleep(5)

    def process_job(self, job):
        print(f"Processing job: {job}")
        nonce = self.solve_job(job)
        if nonce is not None:
            self.submit_result(job, nonce)
        else:
            print("No valid nonce found for the job")
            self.fetch_new_job()

    def fetch_new_job(self):
        print("Fetching new job...")
        while True:
            job = self.get_job()
            if job:
                self.process_job(job)
                break
            else:
                print("Retrying to fetch new job in 5 seconds...")
                time.sleep(5)

    def mine(self):
        initial_job = self.subscribe()
        if initial_job:
            self.process_job(initial_job)

        while True:
            job = self.get_job()
            if job:
                self.process_job(job)
            else:
                print("Failed to retrieve job, retrying in 5 seconds...")
                time.sleep(5)

    def get_job(self):
        self.send({"method": "getjob", "id": 1})
        responses = self.receive()
        for response in responses:
            print("Job response:", response)
            if 'method' in response and response['method'] == 'job':
                return {
                    'blob': response['params']['blob'],
                    'job_id': response['params']['job_id'],
                    'target': response['params']['target'],
                    'seed_hash': response['params']['seed_hash']
                }
        return None

    def solve_job(self, job):
        job_blob = job['blob']
        target = int(job['target'], 16)
        max_attempts = 100000

        for attempt in range(max_attempts):
            nonce = self.generate_nonce()
            nonce_blob = job_blob[:78] + "{:08x}".format(nonce) + job_blob[86:]
            hash_hex = hashlib.sha256(nonce_blob.encode('utf-8')).hexdigest()
            hash_val = int(hash_hex, 16)
            if hash_val < target:
                print(f"Solution found: nonce={nonce}, hash={hash_hex}")
                return nonce

        print(f"No solution found within attempt limit of {max_attempts} attempts")
        return None

    def generate_nonce(self):
        cities = [{'x': self.qprx.mersenne_twister() % 100, 'y': self.qprx.mersenne_twister() % 100} for _ in range(10)]
        sorted_path = dont_matter(cities)
        morton_nonces = [morton_order(city) for city in sorted_path]
        nonce = sum(morton_nonces) & 0xFFFFFFFF
        return nonce

    def submit_result(self, job, nonce):
        result_hash = hashlib.sha256("{:08x}".format(nonce).encode('utf-8')).hexdigest()
        self.send({
            "method": "submit",
            "params": {
                "id": self.miner_id,
                "job_id": job['job_id'],
                "nonce": "{:08x}".format(nonce),
                "result": result_hash
            },
            "id": 1
        })
        responses = self.receive()
        for response in responses:
            print("Submit result:", response)

if __name__ == "__main__":
    miner = XMRMiner("stratum+tcp://xmr.antpool.com:9005", "BadNin.4") 
    try:
        miner.connect()
        miner_thread = threading.Thread(target=miner.mine)
        miner_thread.start()
    except Exception as e:
        print(f"Error connecting to pool: {e}")