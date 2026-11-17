import time
import os
import json

class QPRx2025:
    FILE_SIZE_LIMIT = 25 * 1024 * 1024  # 25MB file size limit

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

    def store_data(self, language, hashed_value, numeric_value):
        # Read current data from file first to ensure up-to-date information
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
                print(f"Similar numeric value found. Adding hash to existing numeric value.")
                if hashed_value not in stored_hashes:
                    stored_hashes.append(hashed_value)
                found = True
                break

        if not found:
            self.data_store[language][numeric_value] = [hashed_value]

        self.store_to_file(language)

    def get_data(self, language, hashed_value):
        # Read current data from file first to ensure up-to-date information
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
                    return numeric_value

        return None

    def delete_data(self, language, hashed_value):
        # Read current data from file first to ensure up-to-date information
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
            f"{line_number}.{char_position}.{ord(char)}"
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

    def encode_text_numeric(self, text):
        encoded_values = self.analyze_characters_and_convert(text)
        compressed_value = ''.join(encoded_values)
        header = str(abs(hash(compressed_value)) % 10**10).zfill(10)
        return header, encoded_values

    def decode_text_numeric(self, language, hashed_value):
        numeric_value = self.get_data(language, hashed_value)
        if numeric_value is None:
            return f"No matching numeric value found for the given hash in {language}."

        encoded_values = numeric_value.split(',')
        decoded_text = [''] * (max(int(value.split('.')[0]) for value in encoded_values) + 1)
        for encoded_char in encoded_values:
            line_number, char_position, char_code = map(int, encoded_char.split('.'))
            if len(decoded_text[line_number]) <= char_position:
                decoded_text[line_number] += ' ' * (char_position - len(decoded_text[line_number]) + 1)
            decoded_text[line_number] = (
                decoded_text[line_number][:char_position] +
                chr(char_code) +
                decoded_text[line_number][char_position + 1:]
            )
        return f"Language: {language}\nDecoded text:\n{'\n'.join(decoded_text)}"

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

        # Update the data with the current in-memory store
        data.update(self.data_store[language])

        with open(file_name, 'w') as f:
            json.dump(data, f)

if __name__ == "__main__":
    code_sample = """
    def example_function("input"):
        print('Hello, world!')
    """
    qprx = QPRx2025()

    language = qprx.detect_language(code_sample)
    numeric_encoded_text, encoded_values = qprx.encode_text_numeric(code_sample)
    hashed_value = qprx.custom_hash(numeric_encoded_text)

    qprx.store_data(language, hashed_value, ','.join(encoded_values))

    decoded_text = qprx.decode_text_numeric(language, hashed_value)
    print(decoded_text)

    queried_text = qprx.decode_text_numeric('Python', 'a9922fc0')
    print(queried_text)

    for lang in ['Python', 'Java', 'C', 'HTML', 'Plain Text']:
        result = qprx.decode_text_numeric(lang, 'a9922fc0')
        if "No matching numeric value found" not in result:
            print(f"Found in {lang}:")
            print(result)
            break
