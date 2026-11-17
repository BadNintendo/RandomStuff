import socket
import json
import time
import hmac
import ssl
from queue import Queue
import threading
from datetime import timedelta
import math
import random

class QPRx2025:
    """Quantum Processing Relay: Instantly query a result!"""
    def __init__(self, seed=None):
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

    def sum_of_sha(self):
        hash_parts = [
            self.lcg() ^ self.mix_entropy(self.lcg()) ^ self.mersenne_twister(),
            self.lcg() ^ self.mix_entropy(self.lcg()) ^ self.mersenne_twister(),
            self.lcg() ^ self.mix_entropy(self.lcg()) ^ self.mersenne_twister(),
            self.lcg() ^ self.mix_entropy(self.lcg()) ^ self.mersenne_twister()
        ]
        return (hash_parts[0] << 96) | (hash_parts[1] << 64) | (hash_parts[2] << 32) | hash_parts[3]

class XMRMiner:
    def __init__(self, pool_url, miner_id, user_agent="xmr-python-miner", api_key=None, api_secret=None, nonce_queue=None):
        self.pool_url = pool_url.replace("stratum+tcp://", "")
        self.miner_id = miner_id
        self.user_agent = user_agent
        self.api_key = api_key
        self.api_secret = api_secret
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.job_id = None
        self.target = None
        self.qprx = QPRx2025(seed=12345)
        self.nonce_queue = nonce_queue if nonce_queue else Queue()
        self.start_time = None
        self.attempts_per_job = 10000

    def log(self, message, color=None):
        colors = {
            "black": "\033[30m",
            "red": "\033[31m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "blue": "\033[34m",
            "magenta": "\033[35m",
            "cyan": "\033[36m",
            "white": "\033[37m",
            "reset": "\033[0m"
        }
        timestamp = time.strftime('%H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        if color and color in colors:
            print(colors[color] + log_message + colors["reset"])
        else:
            print(log_message)

    def connect(self):
        host, port = self.pool_url.split(":")
        attempts = 0
        max_attempts = 5
        while attempts < max_attempts:
            try:
                self.socket.settimeout(30)  # Set a longer timeout for the connection attempt
                self.socket.connect((host, int(port)))
                self.log(f"Connected to pool {self.pool_url}", "green")
                self.log(f"Miner created by BadNintendo. Source: https://github.com/BadNintendo/XMRCrypte", "cyan")
                return
            except socket.timeout:
                self.log(f"Connection attempt {attempts + 1} timed out. Retrying...", "yellow")
            except socket.error as e:
                self.log(f"Socket error during connection attempt {attempts + 1}: {e}", "red")
            attempts += 1
            time.sleep(10)  # Increase the wait time before retrying
        self.log("Failed to connect to the pool after multiple attempts.", "red")

    def send(self, data):
        message = json.dumps(data).encode('utf-8')
        self.socket.sendall(message)
        self.log(f"Sent: {data}", "blue")

    def receive(self):
        data = ""
        while True:
            part = self.socket.recv(4096).decode('utf-8')
            if not part:
                break
            data += part
            try:
                responses = [json.loads(line) for line in data.split('\n') if line]
                return responses
            except json.JSONDecodeError:
                continue

    def get_signature(self):
        nonce = int(time.time() * 1000)
        msg = self.miner_id + self.api_key + str(nonce)
        signature = hmac.new(self.api_secret.encode('utf-8'), msg=msg.encode('utf-8'), digestmod="sha256").hexdigest().upper()
        return signature, nonce

    def send_authenticated_request(self, url, coin_type='XMR'):
        signature, nonce = self.get_signature()
        post_data = {'key': self.api_key, 'nonce': nonce, 'signature': signature, 'coin': coin_type}
        host, port = 'antpool.com', 443
        context = ssl.create_default_context()
        with socket.create_connection((host, port)) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                ssock.sendall(f"POST {url} HTTP/1.1\r\nHost: {host}\r\nContent-Type: application/json\r\nContent-Length: {len(json.dumps(post_data))}\r\n\r\n{json.dumps(post_data)}".encode('utf-8'))
                response = ssock.recv(4096).decode('utf-8')
                headers, body = response.split('\r\n\r\n')
                return body

    def subscribe_and_authenticate(self):
        self.send({
            "id": 1,
            "method": "login",
            "params": {
                "login": self.miner_id,
                "pass": "x",
                "agent": self.user_agent
            }
        })
        response = self.receive()
        self.log(f"Subscription response: {response}", "yellow")

        for res in response:
            if 'result' in res and 'job' in res['result']:
                self.job_id = res['result']['job']['job_id']
                self.target = res['result']['job']['target']
                self.job_blob = res['result']['job']['blob']
                self.seed_hash = res['result']['job']['seed_hash']
                self.log(f"Subscribed and authenticated with job ID: {self.job_id}", "green")
                return res['result']['job']
            elif 'error' in res and res['error']:
                self.log(f"Error during authentication: {res['error']}", "red")
                return None
        self.log("Retrying subscription and authentication in 5 seconds...", "magenta")
        time.sleep(5)
        return self.subscribe_and_authenticate()

    def process_job(self, job):
        self.start_time = time.time()
        self.log(f"Processing job: {job}", "cyan")
        attempts = 0
        while attempts < self.attempts_per_job and not self.nonce_queue.empty():
            nonce = self.nonce_queue.get()
            nonce_blob = job['blob'][:78] + "{:08x}".format(nonce) + job['blob'][86:]
            hash_val = self.qprx.sum_of_sha()
            target = int(job['target'], 16)

            if hash_val < target:
                end_time = time.time()
                duration = timedelta(seconds=end_time - self.start_time)
                duration_str = str(duration)
                self.log(f"Solution found: nonce={nonce}, hash={hash_val}", "green")
                self.log(f"Job completed in {duration_str}", "cyan")
                self.submit_result(job, nonce)
                return

            # Attempt with seed hash
            self.qprx.seed = int(job['seed_hash'], 16)
            hash_val_with_seed = self.qprx.sum_of_sha()
            if hash_val_with_seed < target:
                end_time = time.time()
                duration = timedelta(seconds=end_time - self.start_time)
                duration_str = str(duration)
                self.log(f"Solution found with seed hash: nonce={nonce}, hash={hash_val_with_seed}", "green")
                self.log(f"Job completed in {duration_str}", "cyan")
                self.submit_result(job, nonce)
                return

            attempts += 1

        self.log("No valid nonce found for the job", "red")
        self.fetch_new_job()

    def fetch_new_job(self):
        self.log("Fetching new job...", "magenta")
        while True:
            job = self.get_job()
            if job:
                self.process_job(job)
                break
            else:
                self.log("Failed to retrieve job, retrying in 5 seconds...", "red")
                time.sleep(5)

    def mine(self):
        initial_job = self.subscribe_and_authenticate()
        if initial_job:
            self.process_job(initial_job)
        while True:
            job = self.get_job()
            if job:
                self.process_job(job)
            else:
                self.log("Failed to retrieve job, retrying in 5 seconds...", "red")
                time.sleep(5)

    def get_job(self):
        self.send({"method": "getjob", "id": 1})
        responses = self.receive()
        for response in responses:
            self.log(f"Job response: {response}", "yellow")
            if 'method' in response and response['method'] == 'job':
                return {
                    'blob': response['params']['blob'],
                    'job_id': response['params']['job_id'],
                    'target': response['params']['target'],
                    'seed_hash': response['params']['seed_hash']
                }
        return None

    def submit_result(self, job, nonce):
        result_hash = self.qprx.sum_of_sha()
        self.send({
            "method": "submit",
            "params": {
                "id": self.miner_id,
                "job_id": job['job_id'],
                "nonce": "{:08x}".format(nonce),
                "result": "{:x}".format(result_hash)
            },
            "id": 1
        })
        responses = self.receive()
        for response in responses:
            self.log(f"Submit result: {response}", "yellow")

def producer(nonce_queue, qprx):
    while True:
        nonce = qprx.mersenne_twister()
        nonce_queue.put(nonce)

if __name__ == "__main__":
    nonce_queue = Queue()
    qprx = QPRx2025(seed=12345)
    
    producer_thread = threading.Thread(target=producer, args=(nonce_queue, qprx))
    producer_thread.start()

    miner = XMRMiner(
        "stratum+tcp://xmr.antpool.com:9005", 
        "BadNin.11", 
        api_key="f33b5a1aebc04349a6377d81a0733874", 
        api_secret="0df454dcadc748f7aa5f345c9798eea0",
        nonce_queue=nonce_queue
    )
    try:
        miner.connect()
        miner_thread = threading.Thread(target=miner.mine)
        miner_thread.start()
    except Exception as e:
        print(f"Error connecting to pool: {e}")