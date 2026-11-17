import time
import os
import json

class QRPx2025:
    FILE_SIZE_LIMIT = 25 * 1024 * 1024  # 25MB file size limit
    CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    
    def __init__(self, seed=0):
        """Initialize the QRPx2025 class with a custom seed and set up the data store directory."""
        self.seed = seed % 1000000
        self.entropy = self.mix_entropy(int(time.time() * 1000))
        self.data_store = {}
        self.base_dir = os.path.abspath("data/language_modules")
        os.makedirs(self.base_dir, exist_ok=True)

    def mix_entropy(self, value):
        """Mix entropy to generate a more random initial value."""
        return value ^ (value >> 32) ^ (value >> 16) ^ (value >> 8) ^ value

    def custom_hash(self, input, salt='', hash_val=False):
        """Generate or verify a custom hash using FNV-1a algorithm."""
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
        """Encode a numeric value into a string using a custom character set."""
        if number == 0:
            return self.CHARACTERS[0]
        base = len(self.CHARACTERS)
        result = []
        while number:
            result.append(self.CHARACTERS[number % base])
            number //= base
        return ''.join(reversed(result))

    def decode_numeric(self, string):
        """Decode a string back into a numeric value using a custom character set."""
        base = len(self.CHARACTERS)
        result = 0
        for char in string:
            result = result * base + self.CHARACTERS.index(char)
        return result

    def store_data(self, language, hashed_value, numeric_value):
        """Store hashed data and numeric values, updating files as needed."""
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
        """Retrieve numeric value associated with a hashed value if it exists."""
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
        """Delete a specific hashed value and its associated numeric value."""
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
        """Convert characters of the code into a numeric representation."""
        lines = code.split('\n')
        numeric_representation = [
            f"{line_number}.{char_position}.{self.encode_numeric(ord(char))}"
            for line_number, line in enumerate(lines)
            for char_position, char in enumerate(line)
        ]
        return numeric_representation

    def compare_numeric_values(self, numeric_value1, numeric_value2):
        """Compare two numeric values."""
        return numeric_value1 == numeric_value2

    def detect_language(self, code):
        """Detect the programming language of the given code."""
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
        """Encode text into numeric values and generate a header using a specific seed."""
        encoded_values = self.analyze_characters_and_convert(text)
        compressed_value = ''.join(encoded_values)
        header = str(abs(hash(compressed_value + str(seed))) % 10**10).zfill(10)
        return header, encoded_values

    def decode_text_numeric(self, seed, language, hashed_value):
        """Decode numeric values back into text using the given seed and hashed value."""
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
        """Store the data to a file, ensuring it does not exceed the file size limit."""
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


if __name__ == "__main__":
    code_sample = """
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
"""
    seed_sample = 12345
    qprx = QRPx2025()

    language = qprx.detect_language(code_sample)
    numeric_encoded_text, encoded_values = qprx.encode_text_numeric(seed_sample, code_sample)
    hashed_value = qprx.custom_hash(numeric_encoded_text)

    qprx.store_data(language, hashed_value, ','.join(encoded_values))

    decoded_text = qprx.decode_text_numeric(seed_sample, language, hashed_value)
    print(decoded_text)