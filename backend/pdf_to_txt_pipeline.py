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


from process_pdf_ import ProcessPDF

file_name = 'dr_bernstein_diabetes_solution'
pp = ProcessPDF(file_name)

# pp.extract_pdf_to_text()
# pp.save_pdf_to_txt()

# pp.load_txt()
# pp.clean_text()
# pp.save_clean_text()

# pp.load_clean_text()
# pp.split_text_into_chunks(pp.all_pages_clean_txt)
# pp.save_raw_chunks()

# pp.load_raw_chunks()
# pp.format_chunks()
# pp.save_format_chunks()

# pp.load_format_chunks()
# pp.chunks_to_vectorstore()
# pp.save_vectorestore()