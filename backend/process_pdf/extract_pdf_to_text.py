import json
import pickle
from PyPDF2 import PdfReader, PdfWriter
from langchain_community.document_loaders import UnstructuredPDFLoader
from tqdm import tqdm
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DOCUMENTS_DIR = os.path.join(BASE_DIR, "documents")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMP_PDF_PATH = os.path.join(BASE_DIR, "page_output.pdf")

def extract_pdf_to_text(file_name):
    input_pdf_path = os.path.join(DOCUMENTS_DIR, f"{file_name}.pdf")
    file_output_dir = os.path.join(OUTPUT_DIR, file_name)
    json_output_dir = os.path.join(file_output_dir, "jsons")
    pkl_output_path = os.path.join(file_output_dir, f"{file_name}.pkl")
    txt_output_path = os.path.join(file_output_dir, f"{file_name}.txt")

    os.makedirs(json_output_dir, exist_ok=True)

    reader = PdfReader(input_pdf_path)
    all_documents = []
    
    for page_num in tqdm(range(len(reader.pages))):
        try:
            writer = PdfWriter()
            writer.add_page(reader.pages[page_num])

            with open(TEMP_PDF_PATH, "wb") as f:
                writer.write(f)

            loader = UnstructuredPDFLoader(TEMP_PDF_PATH, strategy="hi_res")
            docs = loader.load()

            page_content = docs[0].page_content

            page_data = {
                "page_number": page_num + 1,
                "content": page_content
            }

            json_path = os.path.join(json_output_dir, f"page_{page_num + 1}.json")
            with open(json_path, 'w') as json_file:
                json.dump(page_data, json_file, indent=4)

            all_documents.append(page_content)

        except Exception as e:
            print(f'Error inside page {page_num + 1}: {e}')

    with open(pkl_output_path, 'wb') as f:
        pickle.dump(all_documents, f)

    with open(txt_output_path, 'w', encoding='utf-8') as f:
        f.write("\n\n".join(all_documents))
    
    os.remove(TEMP_PDF_PATH)
