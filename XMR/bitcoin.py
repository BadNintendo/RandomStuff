import socket
import json
import time
import hmac
import hashlib
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
    def __init__(self, pool_url, miner_id, user_agent="bitcoin-python-miner", api_key=None, api_secret=None):
        self.pool_url = pool_url.replace("stratum+tcp://", "")
        self.miner_id = miner_id
        self.user_agent = user_agent
        self.api_key = api_key
        self.api_secret = api_secret
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.job_id = None
        self.target = None
        self.qprx = QPRx2025(seed=12345)

    def connect(self):
        host, port = self.pool_url.split(":")
        self.socket.connect((host, int(port)))
        print(f"Connected to pool {self.pool_url}")

    def send(self, data):
        message = json.dumps(data).encode('utf-8')
        self.socket.sendall(message)
        print(f"Sent: {data}")

    def receive(self):
        response = self.socket.recv(1024).decode('utf-8').split("\n")
        return [json.loads(line) for line in response if line]

    def get_signature(self):
        nonce = int(time.time() * 1000)
        msg = self.miner_id + self.api_key + str(nonce)
        signature = hmac.new(self.api_secret.encode('utf-8'), msg=msg.encode('utf-8'), digestmod=hashlib.sha256).hexdigest().upper()
        return signature, nonce

    def send_authenticated_request(self, url, coin_type='BTC'):
        signature, nonce = self.get_signature()
        post_data = {'key': self.api_key, 'nonce': nonce, 'signature': signature, 'coin': coin_type}
        request = requests.post(url, data=post_data)
        return request.text

    def subscribe(self):
        self.send({
            "method": "mining.subscribe",
            "params": [self.user_agent],
            "id": 1
        })
        response = self.receive()
        for res in response:
            print("Subscription response:", res)
            if 'result' in res:
                self.job_id = res['result'][1]
                self.target = res['result'][2]
                print(f"Subscribed with job ID: {self.job_id}")
                return res['result']
            elif 'error' in res:
                print(f"Error subscribing: {res['error']}")
                return None

    def authorize(self):
        self.send({
            "method": "mining.authorize",
            "params": [self.miner_id, ""],
            "id": 2
        })
        response = self.receive()
        for res in response:
            print("Authorization response:", res)
            if 'result' in res and res['result']:
                print("Authorized successfully")
                return True
            elif 'error' in res:
                print(f"Authorization error: {res['error']}")
                return False
        return False

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
                print("Failed to retrieve job, retrying in 5 seconds...")
                time.sleep(5)

    def mine(self):
        if self.subscribe() and self.authorize():
            while True:
                job = self.get_job()
                if job:
                    self.process_job(job)
                else:
                    print("Failed to retrieve job, retrying in 5 seconds...")
                    time.sleep(5)

    def get_job(self):
        self.send({"method": "mining.getjob", "id": 3})
        responses = self.receive()
        for response in responses:
            print("Job response:", response)
            if 'method' in response and response['method'] == 'mining.notify':
                return {
                    'job_id': response['params'][0],
                    'prevhash': response['params'][1],
                    'coinb1': response['params'][2],
                    'coinb2': response['params'][3],
                    'merkle_branch': response['params'][4],
                    'version': response['params'][5],
                    'nbits': response['params'][6],
                    'ntime': response['params'][7],
                    'clean_jobs': response['params'][8]
                }
        return None

    def solve_job(self, job):
        max_attempts = 100000
        target = int(job['nbits'], 16)
        coinbase = job['coinb1'] + self.miner_id + job['coinb2']
        merkle_root = self.calculate_merkle_root(coinbase, job['merkle_branch'])
        
        # Prepare block header
        block_header = (
            job['version'] + 
            job['prevhash'] + 
            merkle_root + 
            job['ntime'] + 
            job['nbits']
        )

        for attempt in range(max_attempts):
            nonce = "{:08x}".format(self.generate_nonce())
            block_header_with_nonce = block_header + nonce
            hash_hex = SHA256().update(block_header_with_nonce).digest()
            hash_val = int(hash_hex, 16)
            
            if hash_val < target:
                print(f"Solution found: nonce={nonce}, hash={hash_hex}")
                return nonce
        
        print(f"No solution found within attempt limit of {max_attempts} attempts")
        return None

    def calculate_merkle_root(self, coinbase, merkle_branch):
        merkle_root = coinbase
        for branch in merkle_branch:
            merkle_root = SHA256().update(merkle_root + branch).digest()
        return merkle_root

    def generate_nonce(self):
        cities = [{'x': self.qprx.mersenne_twister() % 100, 'y': self.qprx.mersenne_twister() % 100} for _ in range(10)]
        sorted_path = dont_matter(cities)
        morton_nonces = [morton_order(city) for city in sorted_path]
        nonce = sum(morton_nonces) & 0xFFFFFFFF
        return nonce

    def submit_result(self, job, nonce):
        result_hash = SHA256().update(job['version'] + job['prevhash'] + job['coinb1'] + self.miner_id + job['coinb2'] + job['ntime'] + job['nbits'] + nonce).digest()
        self.send({
            "method": "mining.submit",
            "params": [self.miner_id, job['job_id'], job['ntime'], nonce, result_hash],
            "id": 4
        })
        responses = self.receive()
        for response in responses:
            print("Submit result:", response)

# Example usage
if __name__ == "__main__":
    miner = XMRMiner(
        "stratum+tcp://btc.antpool.com:3333",  # Update to a Bitcoin mining pool
        "BadNin.001", 
        api_key="f33b5a1aebc04349a6377d81a0733874", 
        api_secret="0df454dcadc748f7aa5f345c9798eea0"
    )
    try:
        miner.connect()
        miner_thread = threading.Thread(target=miner.mine)
        miner_thread.start()
    except Exception as e:
        print(f"Error connecting to pool: {e}")