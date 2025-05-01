import os
import json
from process_pdf.extract_pdf_to_text import extract_pdf_to_text
from process_pdf.clean_text import clean_text
from process_pdf.split_text_into_chunks import split_text_into_chunks
from process_pdf.format_chunks import format_chunks

def standards_of_care_2025():
    file_name = 'standards-of-care-2025'
    output_dir = os.path.join('output', file_name)
    os.makedirs(output_dir, exist_ok=True)

    extract_pdf_to_text(file_name=file_name)

    text_path = os.path.join(output_dir, f'{file_name}.txt')
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()

    text = clean_text(text)

    processed_text_path = os.path.join(output_dir, f'{file_name}_processed.txt')
    with open(processed_text_path, 'w', encoding='utf-8') as f:
        f.write(text)

    raw_chunks = split_text_into_chunks(text)

    raw_chunks_path = os.path.join(output_dir, f'{file_name}_chunks.json')
    with open(raw_chunks_path, 'w', encoding='utf-8') as f:
        json.dump(raw_chunks, f, indent=4)

    formatted_chunks = format_chunks(raw_chunks)

    formatted_chunks_path = os.path.join(output_dir, f'{file_name}_chunks-formatted.json')
    with open(formatted_chunks_path, 'w', encoding='utf-8') as f:
        json.dump(formatted_chunks, f, indent=4)


file_name = 'dr_bernstein_diabetes_solution'
output_dir = os.path.join('output', file_name)
os.makedirs(output_dir, exist_ok=True)

all_documents = extract_pdf_to_text(file_name=file_name)

with open(f'{output_dir}/{file_name}.pkl', 'wb') as f:
    pickle.dump(all_documents, f)

with open(f'{output_dir}/{file_name}.txt', 'w', encoding='utf-8') as f:
    f.write("\n\n".join(all_documents))

text_path = os.path.join(output_dir, f'{file_name}.txt')
with open(text_path, 'r', encoding='utf-8') as f:
    text = f.read()

text = clean_text(text)

processed_text_path = os.path.join(output_dir, f'{file_name}_processed.txt')
with open(processed_text_path, 'w', encoding='utf-8') as f:
    f.write(text)

# raw_chunks = split_text_into_chunks(text)

# raw_chunks_path = os.path.join(output_dir, f'{file_name}_chunks.json')
# with open(raw_chunks_path, 'w', encoding='utf-8') as f:
#     json.dump(raw_chunks, f, indent=4)

# formatted_chunks = format_chunks(raw_chunks)

# formatted_chunks_path = os.path.join(output_dir, f'{file_name}_chunks-formatted.json')
# with open(formatted_chunks_path, 'w', encoding='utf-8') as f:
#     json.dump(formatted_chunks, f, indent=4)
