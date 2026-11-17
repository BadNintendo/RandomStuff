import socket
import json
import time

class QPRx2025:
    def __init__(self, seed=0):
        self.seed = seed % 1000000
        self.entropy = self.mix_entropy(int(time.time() * 1000))

    def mix_entropy(self, value):
        return value ^ (value >> 32) ^ (value >> 16) ^ (value >> 8) ^ value

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

# Initialize QPRx2025
qprx = QPRx2025(seed=12345)

# Define the cities data
cities = [
    {'name': 'City0', 'x': 710, 'y': 168},
	{'name': 'City1', 'x': 737, 'y': 137},
	{'name': 'City2', 'x': 761, 'y': 101},
	{'name': 'City3', 'x': 661, 'y': 125},
	{'name': 'City4', 'x': 707, 'y': 185},
	{'name': 'City5', 'x': 612, 'y': 126},
	{'name': 'City6', 'x': 682, 'y': 198},
	{'name': 'City7', 'x': 829, 'y': 137},
	{'name': 'City8', 'x': 673, 'y': 190},
	{'name': 'City9', 'x': 567, 'y': 156},
	{'name': 'City10', 'x': 619, 'y': 119},
	{'name': 'City11', 'x': 594, 'y': 100},
	{'name': 'City12', 'x': 550, 'y': 100},
	{'name': 'City13', 'x': 734, 'y': 108},
	{'name': 'City14', 'x': 836, 'y': 178},
	{'name': 'City15', 'x': 883, 'y': 199},
	{'name': 'City16', 'x': 646, 'y': 137},
	{'name': 'City17', 'x': 732, 'y': 170},
	{'name': 'City18', 'x': 880, 'y': 178},
	{'name': 'City19', 'x': 590, 'y': 118},
	{'name': 'City20', 'x': 501, 'y': 182},
	{'name': 'City21', 'x': 504, 'y': 141},
	{'name': 'City22', 'x': 814, 'y': 104},
	{'name': 'City23', 'x': 651, 'y': 142},
	{'name': 'City24', 'x': 688, 'y': 118},
	{'name': 'City25', 'x': 637, 'y': 162},
	{'name': 'City26', 'x': 875, 'y': 141},
	{'name': 'City27', 'x': 717, 'y': 170},
	{'name': 'City28', 'x': 781, 'y': 154},
	{'name': 'City29', 'x': 861, 'y': 178},
	{'name': 'City30', 'x': 795, 'y': 178},
	{'name': 'City31', 'x': 500, 'y': 155},
	{'name': 'City32', 'x': 581, 'y': 127},
	{'name': 'City33', 'x': 822, 'y': 131},
	{'name': 'City34', 'x': 594, 'y': 193},
	{'name': 'City35', 'x': 708, 'y': 172},
	{'name': 'City36', 'x': 655, 'y': 145},
	{'name': 'City37', 'x': 581, 'y': 165},
	{'name': 'City38', 'x': 518, 'y': 174},
	{'name': 'City39', 'x': 771, 'y': 133},
	{'name': 'City40', 'x': 660, 'y': 131},
	{'name': 'City41', 'x': 505, 'y': 134},
	{'name': 'City42', 'x': 871, 'y': 128},
	{'name': 'City43', 'x': 686, 'y': 154},
	{'name': 'City44', 'x': 771, 'y': 117},
	{'name': 'City45', 'x': 782, 'y': 182},
	{'name': 'City46', 'x': 849, 'y': 164},
	{'name': 'City47', 'x': 723, 'y': 145},
	{'name': 'City48', 'x': 735, 'y': 198},
	{'name': 'City49', 'x': 679, 'y': 125},
	{'name': 'City50', 'x': 594, 'y': 101},
	{'name': 'City51', 'x': 829, 'y': 138},
	{'name': 'City52', 'x': 862, 'y': 111},
	{'name': 'City53', 'x': 898, 'y': 105},
	{'name': 'City54', 'x': 695, 'y': 128},
	{'name': 'City55', 'x': 725, 'y': 139},
	{'name': 'City56', 'x': 662, 'y': 108},
	{'name': 'City57', 'x': 682, 'y': 167},
	{'name': 'City58', 'x': 549, 'y': 177},
	{'name': 'City59', 'x': 574, 'y': 168},
	{'name': 'City60', 'x': 536, 'y': 145},
	{'name': 'City61', 'x': 891, 'y': 117},
	{'name': 'City62', 'x': 802, 'y': 159},
	{'name': 'City63', 'x': 772, 'y': 193},
	{'name': 'City64', 'x': 584, 'y': 145},
	{'name': 'City65', 'x': 775, 'y': 140},
	{'name': 'City66', 'x': 702, 'y': 158},
	{'name': 'City67', 'x': 864, 'y': 100},
	{'name': 'City68', 'x': 733, 'y': 163},
	{'name': 'City69', 'x': 804, 'y': 136},
	{'name': 'City70', 'x': 568, 'y': 173},
	{'name': 'City71', 'x': 697, 'y': 135},
	{'name': 'City72', 'x': 891, 'y': 185},
	{'name': 'City73', 'x': 731, 'y': 129},
	{'name': 'City74', 'x': 538, 'y': 116},
	{'name': 'City75', 'x': 735, 'y': 148},
	{'name': 'City76', 'x': 630, 'y': 173},
	{'name': 'City77', 'x': 713, 'y': 117},
	{'name': 'City78', 'x': 802, 'y': 160},
	{'name': 'City79', 'x': 700, 'y': 132},
	{'name': 'City80', 'x': 691, 'y': 111},
	{'name': 'City81', 'x': 694, 'y': 130},
	{'name': 'City82', 'x': 600, 'y': 104},
	{'name': 'City83', 'x': 767, 'y': 179},
	{'name': 'City84', 'x': 882, 'y': 155},
	{'name': 'City85', 'x': 771, 'y': 193},
	{'name': 'City86', 'x': 731, 'y': 147},
	{'name': 'City87', 'x': 661, 'y': 135},
	{'name': 'City88', 'x': 597, 'y': 176},
	{'name': 'City89', 'x': 600, 'y': 151},
	{'name': 'City90', 'x': 712, 'y': 108},
	{'name': 'City91', 'x': 667, 'y': 189},
	{'name': 'City92', 'x': 529, 'y': 162},
	{'name': 'City93', 'x': 710, 'y': 182},
	{'name': 'City94', 'x': 782, 'y': 168},
	{'name': 'City95', 'x': 648, 'y': 126},
	{'name': 'City96', 'x': 664, 'y': 135},
	{'name': 'City97', 'x': 777, 'y': 187},
	{'name': 'City98', 'x': 535, 'y': 162},
	{'name': 'City99', 'x': 611, 'y': 129},
	{'name': 'City100', 'x': 530, 'y': 105}
]

# JSON encode the cities data and calculate the hash
cities_data = json.dumps(cities).encode('utf-8')
hash_value = qprx.custom_hash(cities_data.decode('utf-8'))
request_data = json.dumps({'data': cities, 'hash': hash_value}).encode('utf-8')

def client():
    first_response = None
    protocols = ['TCP', 'UDP']
    results = {}

    for protocol in protocols:
        if first_response:
            break
        
        try:
            start_time = time.time()
            if protocol == 'TCP':
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(('127.0.0.1', 3000))
                print(f"Encoded Values: {request_data}")
                sock.sendall(request_data)
                data = sock.recv(4096)
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                server_address = ('127.0.0.1', 3000)
                print(f"Encoded Values: {request_data}")
                sock.sendto(request_data, server_address)
                data, _ = sock.recvfrom(4096)
            end_time = time.time()
            processing_time = round((end_time - start_time) * 1000, 2)
            response = json.loads(data.decode('utf-8'))

            if not first_response:
                first_response = protocol
                results['response'] = response

        except Exception as e:
            if not first_response:
                first_response = protocol
                results['error'] = str(e)
        finally:
            if 'sock' in locals():
                sock.close()
    
    if 'response' in results:
        first_city = results['response'][0]
        second_to_last_city = results['response'][-2]
        last_city = results['response'][-1]
        print(f"First starting point: {first_city}")
        print(f"Second-to-last starting point: {second_to_last_city}")
        print(f"Last starting point: {last_city}")

# Execute the client function
print("Sending data using TCP and UDP...")
client()