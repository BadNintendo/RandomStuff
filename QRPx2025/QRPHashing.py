import time
import math

class QPRx2025:
    def __init__(self, seed=0):
        self.seed = seed % 1000000
        self.entropy = self.mix_entropy(int(time.time() * 1000))
        self.data_store = {}

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

        def verify_hash(self, input, salt, hashed):
            return hashing(input, salt) == hashed

        if isinstance(hash_val, str):
            return verify_hash(input, salt, hash_val)
        return hashing(input, salt)

    def store_data(self, hashed_value, numeric_value):
        self.data_store[hashed_value] = numeric_value

    def get_data(self, hashed_value):
        return self.data_store.get(hashed_value, None)

    def delete_data(self, hashed_value):
        if hashed_value in self.data_store:
            del self.data_store[hashed_value]
            return True
        return False

    def analyze_characters_and_convert(self, code):
        report = []
        numeric_representation = []
        lines = code.split('\n')

        for line_number, line in enumerate(lines):
            for char_position, char in enumerate(line):
                encoded_char = f"{line_number}.{char_position}.{ord(char)}"
                report.append(f'Character "{char}" at {encoded_char}')
                numeric_representation.append(encoded_char)
        return report, numeric_representation

    def detect_language_and_analyze(self, code):
        if 'def ' in code or 'import ' in code:
            language = 'Python'
        elif 'class ' in code or 'public static void main' in code:
            language = 'Java'
        elif '#include' in code or 'int main' in code:
            language = 'C'
        elif '<' in code and '>' in code:
            language = 'HTML'
        else:
            language = 'Plain Text'

        print(f"Detected language: {language}")

        char_analysis, numeric_representation = self.analyze_characters_and_convert(code)
        print("Character encoding analysis:")
        for item in char_analysis:
            print(item)
        print("Numeric representation:")
        for num_rep in numeric_representation:
            print(num_rep)

    def encode_text_numeric(self, text):
        lines = text.split('\n')
        encoded_values = []

        for line_number, line in enumerate(lines):
            for char_position, char in enumerate(line):
                encoded_values.append(f"{line_number}.{char_position}.{ord(char)}")

        compressed_value = ''.join(encoded_values)
        header = str(int(math.fabs(hash(compressed_value))) % (10**10)).zfill(10)
        
        return header, encoded_values

    def decode_text_numeric(self, hashed_value):
        numeric_value = self.get_data(hashed_value)
        if numeric_value is None:
            return "No matching numeric value found for the given hash."

        encoded_values = numeric_value.split(',')
        decoded_text = [''] * (max(int(value.split('.')[0]) for value in encoded_values) + 1)
        for encoded_char in encoded_values:
            line_number, char_position, char_code = encoded_char.split('.')
            line_number = int(line_number)
            char_position = int(char_position)
            char = chr(int(char_code))
            if len(decoded_text[line_number]) < char_position:
                decoded_text[line_number] += ' ' * (char_position - len(decoded_text[line_number]))
            decoded_text[line_number] = decoded_text[line_number][:char_position] + char + decoded_text[line_number][char_position + 1:]
        
        return '\n'.join(decoded_text)

# Test input, encoding, and decoding
if __name__ == "__main__":
    code_sample = """
    def example_function():
        print('Hello, world!')
    """
    qprx = QPRx2025()
    
    qprx.detect_language_and_analyze(code_sample)
    
    numeric_encoded_text, encoded_values = qprx.encode_text_numeric(code_sample)
    print(f"Numeric encoded text: {numeric_encoded_text}")
    
    del code_sample

    hashed_value = qprx.custom_hash(numeric_encoded_text)
    print(f"Hashed value: {hashed_value}")

    qprx.store_data(hashed_value, ','.join(encoded_values))

    decoded_text = qprx.decode_text_numeric(hashed_value)
    print(f"Decoded text: {decoded_text}")

    delete_result = qprx.delete_data(hashed_value)
    print(f"Deleted hash: {delete_result}")

    decoded_text_after_deletion = qprx.decode_text_numeric(hashed_value)
    print(f"Decoded text after deletion: {decoded_text_after_deletion}")
