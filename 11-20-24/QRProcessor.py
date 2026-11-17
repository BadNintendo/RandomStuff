import time
import os
import json

class QRPx2025:
    FILE_SIZE_LIMIT = 25 * 1024 * 1024  # 25MB file size limit
    CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

    def __init__(self, seed=0):
        self.seed = seed % 1000000
        self.entropy = self.mix_entropy(int(time.time() * 1000))
        self.data_store = {}
        self.base_dir = os.path.abspath("data/language_modules")
        os.makedirs(self.base_dir, exist_ok=True)

    def mix_entropy(self, value):
        return value ^ (value >> 32) ^ (value >> 16) ^ (value >> 8) ^ value

    def custom_hash(self, input, salt='', hash_val=False):
        def hashing(input, salt):
            combined = f'{input}{salt}'
            hashed = 0x811c9dc5
            for char in combined:
                hashed ^= ord(char)
                hashed = (hashed * 0x01000193) % (2 ** 32)
            return f'{hashed:08x}'

        def verify_hash(input, salt, hashed):
            return hashing(input, salt) == hashed

        if isinstance(hash_val, str):
            return verify_hash(input, salt, hash_val)
        return hashing(input, salt)

    def encode_numeric(self, number):
        if number == 0:
            return self.CHARACTERS[0]
        base = len(self.CHARACTERS)
        result = []
        while number:
            result.append(self.CHARACTERS[number % base])
            number //= base
        return ''.join(reversed(result))

    def decode_numeric(self, string):
        base = len(self.CHARACTERS)
        result = 0
        for char in string:
            result = result * base + self.CHARACTERS.index(char)
        return result

    def store_data(self, language, hashed_value, numeric_value):
        file_index = 0
        while True:
            file_name = os.path.join(self.base_dir, f"{language}_{file_index}.json")
            if not os.path.exists(file_name):
                break
            with open(file_name, 'r') as f:
                data = json.load(f)
                self.data_store[language] = data
            file_index += 1

        if language not in self.data_store:
            self.data_store[language] = {}

        found = False
        for stored_numeric, stored_hashes in self.data_store[language].items():
            if self.compare_numeric_values(stored_numeric, numeric_value):
                if hashed_value not in stored_hashes:
                    stored_hashes.append(hashed_value)
                found = True
                break

        if not found:
            self.data_store[language][numeric_value] = [hashed_value]

        self.store_to_file(language)

    def get_data(self, language, hashed_value):
        file_index = 0
        while True:
            file_name = os.path.join(self.base_dir, f"{language}_{file_index}.json")
            if not os.path.exists(file_name):
                break
            with open(file_name, 'r') as f:
                data = json.load(f)
                self.data_store[language] = data
            file_index += 1

        if language in self.data_store:
            for numeric_value, hashes in self.data_store[language].items():
                if hashed_value in hashes:
                    return numeric_value, True

        return None, False

    def delete_data(self, language, hashed_value):
        file_index = 0
        while True:
            file_name = os.path.join(self.base_dir, f"{language}_{file_index}.json")
            if not os.path.exists(file_name):
                break
            with open(file_name, 'r') as f:
                data = json.load(f)
                self.data_store[language] = data
            file_index += 1

        if language in self.data_store:
            for numeric_value in list(self.data_store[language]):
                hashes = self.data_store[language][numeric_value]
                if hashed_value in hashes:
                    hashes.remove(hashed_value)
                    if not hashes:
                        del self.data_store[language][numeric_value]
                    self.store_to_file(language)
                    return True
        return False

    def analyze_characters_and_convert(self, code):
        lines = code.split('\n')
        numeric_representation = [
            f"{line_number}.{char_position}.{self.encode_numeric(ord(char))}"
            for line_number, line in enumerate(lines)
            for char_position, char in enumerate(line)
        ]
        return numeric_representation

    def compare_numeric_values(self, numeric_value1, numeric_value2):
        return numeric_value1 == numeric_value2

    def detect_language(self, code):
        if 'def ' in code or 'import ' in code:
            return 'Python'
        elif 'class ' in code or 'public static void main' in code:
            return 'Java'
        elif '#include' in code or 'int main' in code:
            return 'C'
        elif '<' in code and '>' in code:
            return 'HTML'
        else:
            return 'Plain Text'

    def encode_text_numeric(self, seed, text):
        encoded_values = self.analyze_characters_and_convert(text)
        compressed_value = ''.join(encoded_values)
        header = str(abs(hash(compressed_value + str(seed))) % 10**10).zfill(10)
        return header, encoded_values

    def decode_text_numeric(self, seed, language, hashed_value):
        numeric_value, hash_found = self.get_data(language, hashed_value)
        if not hash_found:
            return f"Hash: Not found, Value: Not found in {language}."

        encoded_values = numeric_value.split(',')
        decoded_text = [''] * (max(int(value.split('.')[0]) for value in encoded_values) + 1)
        for encoded_char in encoded_values:
            line_number, char_position, char_code = encoded_char.split('.')
            char_code = self.decode_numeric(char_code)
            line_number = int(line_number)
            char_position = int(char_position)
            if len(decoded_text[line_number]) <= char_position:
                decoded_text[line_number] += ' ' * (char_position - len(decoded_text[line_number]) + 1)
            decoded_text[line_number] = (
                decoded_text[line_number][:char_position] +
                chr(char_code) +
                decoded_text[line_number][char_position + 1:]
            )
        return f"Hash: Found, Value: Found in {language}\nDecoded text:\n{'\n'.join(decoded_text)}"

    def store_to_file(self, language):
        file_index = 0
        while True:
            file_name = os.path.join(self.base_dir, f"{language}_{file_index}.json")
            if not os.path.exists(file_name) or os.path.getsize(file_name) < self.FILE_SIZE_LIMIT:
                break
            file_index += 1

        data = {}
        if os.path.exists(file_name):
            with open(file_name, 'r') as f:
                data = json.load(f)

        data.update(self.data_store[language])

        with open(file_name, 'w') as f:
            json.dump(data, f)

    def quantum_polls_relay(self, max_val):
        if not isinstance(max_val, int) or max_val <= 0:
            raise ValueError('Invalid max value for QuantumPollsRelay')
        lcg_value = self.lcg()
        mt_value = self.mersenne_twister()
        return ((lcg_value + mt_value) % 1000000) % max_val

    def lcg(self, a=None, c=None, m=None):
        if self.seed is None or self.entropy is None:
            raise ValueError('Seed and entropy must be initialized to use LCG')
        a, c, m = a or self.LCG_PARAMS['a'], c or self.LCG_PARAMS['c'], m or self.LCG_PARAMS['m']
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

    def dont_matter(self, cities):
        if not cities:
            print("No cities to process. Please check the input data.")
            return []

        def interleave_bits(x, y):
            def spread_bits(v):
                v = (v | (v << 8)) & 0x00FF00FF
                v = (v | (v << 4)) & 0x0F0F0F0F
                v = (v | (v << 2)) & 0x33333333
                v = (v | (v << 1)) & 0x55555555
                return v

            return spread_bits(x) | (spread_bits(y) << 1)

        def morton_order(city):
            x = int(city['x'] * 10000)
            y = int(city['y'] * 10000)
            return interleave_bits(x, y)

        start_sort_time = time.time()
        cities_sorted = sorted(cities, key=morton_order)
        sorted_path = [cities_sorted.pop(0)]
        cities_sorted.sort(key=lambda city: (city['x'], city['y']))
        sorted_path.extend(cities_sorted)
        sorted_path.append(sorted_path[0])
        end_sort_time = time.time()
        sort_time = round((end_sort_time - start_sort_time) * 1000, 2)
        print(f"Sort Time (ms): {sort_time}")
        return sorted_path

    def xor_cipher(self, input, key):
        return ''.join(chr(ord(input[i]) ^ ord(key[i % len(key)])) for i in range(len(input)))

    def generate_uuid(self):
        bytes_array = [self.mersenne_twister() + self.quantum_polls_relay(256) & 0xff for _ in range(16)]
        bytes_array[6] = (bytes_array[6] & 0x0f) | 0x40
        bytes_array[8] = (bytes_array[8] & 0x3f) | 0x80
        uuid = ''.join(f'{b:02x}' for b in bytes_array)
        return f'{uuid[:8]}-{uuid[8:12]}-{uuid[12:16]}-{uuid[16:20]}-{uuid[20:]}'