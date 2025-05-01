from process_pdf.extract_pdf_to_text import extract_pdf_to_text
from process_pdf.clean_text import clean_text
from process_pdf.split_text_into_chunks import split_text_into_chunks
from process_pdf.format_chunks import format_chunks

# extract_pdf_to_text(file_name = 'standards-of-care-2025')

with open('output/standards-of-care-2025.txt', 'r', encoding='utf-8') as f:
    text = f.read()

text = clean_text(text)

with open('output/processed-standards-of-care-2025.txt', 'w', encoding='utf-8') as f:
    f.write(text)

raw_chunks = split_text_into_chunks(text)

with open('output/standards-of-care-2025-chunks.json', 'w') as f:
    json.dump(raw_chunks, f, indent=4)

formatted_chunks = format_chunks(raw_chunks)

with open('output/standards-of-care-2025-chunks-formatted.json', 'w') as f:
    json.dump(formatted_chunks, f, indent=4)