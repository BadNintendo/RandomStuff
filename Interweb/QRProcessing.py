import math

# Function to analyze characters and convert to numeric format
def analyze_characters_and_convert(code):
    special_chars = ['"', "'", '(', ')', '{', '}', '[', ']', '<', '>', ',', ';', ':', '->', '=>']
    report = []
    numeric_representation = []
    lines = code.split('\n')

    for line_number, line in enumerate(lines):
        for char_position, char in enumerate(line):
            encoded_char = f"{line_number}.{char_position}.{ord(char)}"
            report.append(f'Character "{char}" at {encoded_char}')
            numeric_representation.append(encoded_char)
    return report, numeric_representation

# Main language detection and comparison function
def detect_language_and_analyze(code):
    # Determine language based on content
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

    # Log the results
    print(f"Detected language: {language}")

    # Encode characters and convert to numeric representation
    char_analysis, numeric_representation = analyze_characters_and_convert(code)
    print("Character encoding analysis:")
    for item in char_analysis:
        print(item)
    print("Numeric representation:")
    for num_rep in numeric_representation:
        print(num_rep)

# Custom numeric encoding function to compress into 10 digits
def encode_text_numeric(text):
    lines = text.split('\n')
    encoded_values = []

    for line_number, line in enumerate(lines):
        for char_position, char in enumerate(line):
            encoded_values.append(f"{line_number}.{char_position}.{ord(char)}")

    # Compress numeric representation into a single value
    compressed_value = ''.join(encoded_values)
    # Generate a 10-digit hash of the compressed value
    header = str(int(math.fabs(hash(compressed_value))) % (10**10)).zfill(10)
    
    return header, encoded_values

# Custom numeric decoding function using the 10-digit hash and encoded values
def decode_text_numeric(header, encoded_values):
    # For demonstration purposes, assume original text is regenerated
    # In practice, you need a way to map the 10-digit header back to encoded values
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
        print("Hello, world!")
    """
    detect_language_and_analyze(code_sample)
    
    numeric_encoded_text, encoded_values = encode_text_numeric(code_sample)
    print(f"Numeric encoded text: {numeric_encoded_text}")
    
    # To demonstrate, assume encoded values are mapped back from the header
    # In reality, the mapping needs to be maintained externally
    decoded_text = decode_text_numeric(numeric_encoded_text, encoded_values)
    print(f"Decoded text: {decoded_text}")
