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
                encoded_char = f"{line_number}.{char_position + 1}"
                report.append(f'Character "{char}" at {encoded_char}')
                numeric_representation.append(encoded_char)
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

# Custom numeric encoding function
def encode_text_numeric(text):
    numeric_encoded = []
    lines = text.split('\n')
    for line_number, line in enumerate(lines):
        for char_position, char in enumerate(line):
            numeric_encoded.append(f"{line_number}.{char_position}.{ord(char)}")
    return ' '.join(numeric_encoded)

# Custom numeric decoding function
def decode_text_numeric(encoded_text):
    decoded_text = []
    numeric_encoded = encoded_text.split(' ')
    lines = {}
    for token in numeric_encoded:
        line_number, char_position, char_code = token.split('.')
        line_number = int(line_number)
        char_position = int(char_position)
        char_code = int(char_code)
        if line_number not in lines:
            lines[line_number] = {}
        lines[line_number][char_position] = chr(char_code)

    for line_number in sorted(lines.keys()):
        line_chars = [lines[line_number][i] if i in lines[line_number] else ' ' for i in range(max(lines[line_number].keys()) + 1)]
        decoded_text.append(''.join(line_chars))

    return '\n'.join(decoded_text)

# Test input, encoding, and decoding
if __name__ == "__main__":
    code_sample = """
    def example_function():
        print("Hello, world!")
    """
    detect_language_and_analyze(code_sample)
    
    numeric_encoded_text = encode_text_numeric(code_sample)
    print(f"Numeric encoded text: {numeric_encoded_text}")

    decoded_text = decode_text_numeric(numeric_encoded_text)
    print(f"Decoded text: {decoded_text}")