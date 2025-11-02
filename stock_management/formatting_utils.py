import unicodedata

def normalize_text(text):
    # Remove accents
    text = unicodedata.normalize('NFKD', text)
    text = ''.join([c for c in text if not unicodedata.combining(c)])
    # Lowercase
    text = text.lower()
    # Replace decimal comma with dot (only if surrounded by digits)
    text = text.replace(',', '.')
    # Remove extra spaces
    text = ' '.join(text.split())
    return text.strip()


def process_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    processed = set()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Replace decimal comma with dot only if surrounded by digits
        import re
        line = re.sub(r'(\d),(\d)', r'\1.\2', line)
        norm = normalize_text(line)
        processed.add(norm)

    sorted_drugs = sorted(processed)
    with open(output_path, 'w', encoding='utf-8') as f:
        for drug in sorted_drugs:
            f.write(drug + '\n')