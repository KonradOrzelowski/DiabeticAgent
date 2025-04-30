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

    TEMP_PDF_PATH = TEMP_PDF_PATH
    reader = PdfReader(f"{DOCUMENTS_DIR}/{file_name}.pdf")

    all_documents = []
    
    for page_num in tqdm(range(len(reader.pages))):
        try:
            # Create a new PDF writer for the current page
            writer = PdfWriter()
            writer.add_page(reader.pages[page_num])

            # Write the current page to a temporary PDF file
            with open(TEMP_PDF_PATH, "wb") as f:
                writer.write(f)

            # Load the content of the current page using UnstructuredPDFLoader
            loader = UnstructuredPDFLoader(TEMP_PDF_PATH=TEMP_PDF_PATH, strategy="hi_res") 
            docs = loader.load()

            # Extract content from the page
            page_content = docs[0].page_content

            # Prepare the data to be saved as JSON
            page_data = {
                "page_number": page_num,
                "content": page_content
            }
            
            os.makedirs(f'{OUTPUT_DIR}/{file_name}', exist_ok=True)
            os.makedirs(f'{OUTPUT_DIR}/{file_name}/jsons', exist_ok=True)

            # Save the page content into a separate JSON file
            with open(f'{OUTPUT_DIR}/{file_name}/jsons/page_{page_num + 1}.json', 'w') as json_file:
                json.dump(page_data, json_file, indent=4)
            all_documents.append(page_content)
        except Exception as e:
            print(f'Error inside page {page_num}: {e}')

    with open(f'{OUTPUT_DIR}/{file_name}/{file_name}.pkl', 'wb') as f:
        pickle.dump(all_documents, f)

    with open(f'{OUTPUT_DIR}/{file_name}/{file_name}.txt', 'w', encoding='utf-8') as f:
        f.write(all_documents)
    
    # Clean up temporary PDF file
    os.remove(TEMP_PDF_PATH)



# extract_pdf_to_text(file_name = 'standards-of-care-2025')