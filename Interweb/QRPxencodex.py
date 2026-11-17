# Define a custom encoder for characters
def custom_encoder(char):
    encoding_map = {
        '"': 'ENC_DBL_QUOTE',
        "'": 'ENC_SGL_QUOTE',
        '(': 'ENC_OPEN_PAREN',
        ')': 'ENC_CLOSE_PAREN',
        '{': 'ENC_OPEN_CURLY',
        '}': 'ENC_CLOSE_CURLY',
        '[': 'ENC_OPEN_BRACKET',
        ']': 'ENC_CLOSE_BRACKET',
        '<': 'ENC_OPEN_ANGLE',
        '>': 'ENC_CLOSE_ANGLE',
        ',': 'ENC_COMMA',
        ';': 'ENC_SEMICOLON',
        ':': 'ENC_COLON',
        '->': 'ENC_ARROW',
        '=>': 'ENC_FAT_ARROW'
    }
    return encoding_map.get(char, f'ENC_UNKNOWN_{char}')

# Base function to analyze characters and convert to numeric format
def analyze_characters_and_convert(code):
    special_chars = ['"', "'", '(', ')', '{', '}', '[', ']', '<', '>', ',', ';', ':', '->', '=>']
    report = []
    numeric_representation = []
    lines = code.split('\n')

    for line_number, line in enumerate(lines):
        current_position = 0
        for char_position, char in enumerate(line):
            if any(char in sc for sc in special_chars):
                encoded_char = custom_encoder(char)
                numeric_value = f"{line_number}.{current_position}.{char_position + 1}"
                report.append(f'Character "{char}" encoded as {encoded_char} at {numeric_value}')
                numeric_representation.append(numeric_value)
                current_position += 1
        if not line.strip():
            current_position = 0
    return report, numeric_representation

# Language-specific analyzers
def analyze_python(code):
    if '"' in code or "'" in code:
        return "Python-specific quotes detected"
    if '->' in code:
        return "Python-specific arrow function detected"
    return "No Python-specific patterns found"

def analyze_java(code):
    if 'class ' in code or 'public static void main' in code:
        return "Java code detected"
    if '->' in code or '=>' in code:
        return "Java arrow function detected"
    return "No Java-specific patterns found"

def analyze_c(code):
    if '#include' in code or 'int main' in code:
        return "C code detected"
    if '->' in code:
        return "C arrow function detected"
    return "No C-specific patterns found"

def analyze_html(code):
    if '<' in code and '>' in code:
        return "HTML tag structure detected"
    return "No HTML-specific patterns found"

def analyze_plain_text(code):
    return "Plain text detected; no programming language patterns"

# Main language detection and comparison function
def detect_language_and_analyze(code):
    # Determine language based on content
    if 'def ' in code or 'import ' in code:
        language = 'Python'
        analysis = analyze_python(code)
    elif 'class ' in code or 'public static void main' in code:
        language = 'Java'
        analysis = analyze_java(code)
    elif '#include' in code or 'int main' in code:
        language = 'C'
        analysis = analyze_c(code)
    elif '<' in code and '>' in code:
        language = 'HTML'
        analysis = analyze_html(code)
    else:
        language = 'Plain Text'
        analysis = analyze_plain_text(code)

    # Log the results
    print(f"Detected language: {language}")
    print(f"Analysis: {analysis}")

    # Encode characters and convert to numeric representation
    char_analysis, numeric_representation = analyze_characters_and_convert(code)
    print("Character encoding analysis:")
    for item in char_analysis:
        print(item)
    print("Numeric representation:")
    for num_rep in numeric_representation:
        print(num_rep)

# Custom character encoding function using "abc" as a key
def encode_character(char, key):
    key_map = {'a': 1, 'b': 2, 'c': 3}
    return chr(ord(char) + key_map[key])

def encode_text(text, key_sequence):
    encoded = ''
    for index, char in enumerate(text):
        key = key_sequence[index % len(key_sequence)]
        encoded += encode_character(char, key)
    return encoded

# Custom character decoding function using "abc" as a key
def decode_character(char, key):
    key_map = {'a': 1, 'b': 2, 'c': 3}
    return chr(ord(char) - key_map[key])

def decode_text(text, key_sequence):
    decoded = ''
    for index, char in enumerate(text):
        key = key_sequence[index % len(key_sequence)]
        decoded += decode_character(char, key)
    return decoded

# Test input, encoding, and decoding
if __name__ == "__main__":
    code_sample = """
    def example_function():
        print("Hello, world!")
    """
    detect_language_and_analyze(code_sample)
    
    key_sequence = "abc"
    encoded_text = encode_text(code_sample, key_sequence)
    print(f"Encoded text: {encoded_text}")

    decoded_text = decode_text(encoded_text, key_sequence)
    print(f"Decoded text: {decoded_text}")