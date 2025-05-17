import os
import re
import json
import pickle
import openai
import wordninja
import unicodedata

from tqdm import tqdm

from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings

from chunking_evaluation.chunking import (
    LLMSemanticChunker,
    ClusterSemanticChunker
)
from chromadb.utils import embedding_functions


def openai_token_count(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string, disallowed_special=()))
    return num_tokens

class ProcessPDF:
    """
    A class for extracting, cleaning, chunking, and formatting text from a PDF file using OpenAI and LangChain tools.

    Attributes:
        file_name (str): The name of the input PDF file (without extension).
        all_pages (list): List of raw text from each PDF page.
        all_pages_txt (str): Concatenated raw text from all pages.
        all_pages_clean_txt (str): Cleaned and processed text.
        raw_chunks (dict): Dictionary of semantically split text chunks.
        formatted_chunks (dict): Dictionary of formatted chunks.
    """
    def __init__(self, file_name, origin_type = 'pdf'):
        self.file_name = file_name
        self.origin_type = 'pdf'

        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # PDF location which will be processed
        self.documents_dir = os.path.join(self.base_dir, "documents")
        self.input_pdf_path = os.path.join(self.documents_dir, f"{file_name}.pdf")

        # Output dir
        self.output_dir = os.path.join(self.base_dir, "output")
        self.temp_pdf_path = os.path.join(self.base_dir, "page_output.pdf")
        self.file_output_dir = os.path.join(self.output_dir, self.file_name)

        self.json_output_dir = os.path.join(self.file_output_dir, "jsons")
        self.pkl_output_path = os.path.join(self.file_output_dir, f"{self.file_name}.pkl")
        self.txt_output_path = os.path.join(self.file_output_dir, f"{self.file_name}.txt")
        self.txt_output_processed_path = os.path.join(self.file_output_dir, f"{self.file_name}_processed.txt")

        self.chunk_json_output_path = os.path.join(self.file_output_dir, f"{self.file_name}_chunks.json")
        self.chunk_json_formatted_output_path = os.path.join(self.file_output_dir, f"{self.file_name}_chunks_formatted.json")

        self.vec_output_path = os.path.join(self.file_output_dir, f"{self.file_name}_vectorstore")

        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.embeddings = OpenAIEmbeddings()

        self.all_pages = None
        self.all_pages_txt = None
        self.all_pages_clean_txt = None
        self.raw_chunks = None
        self.formatted_chunks = None
        self.vectorstore = None


    def extract_pdf_to_text(self):
        """
        Extracts text from each page of the input PDF using UnstructuredPDFLoader.

        Returns:
            list: A list of strings, each representing a page's content.
        """
        reader = PdfReader(self.input_pdf_path)
        self.all_pages = []
        
        for page_num in tqdm(range(len(reader.pages))):
            try:
                writer = PdfWriter()
                writer.add_page(reader.pages[page_num])

                with open(self.temp_pdf_path, "wb") as f:
                    writer.write(f)

                loader = UnstructuredPDFLoader(self.temp_pdf_path, strategy="hi_res")
                docs = loader.load()

                page_content = docs[0].page_content

                page_data = {
                    "page_number": page_num + 1,
                    "content": page_content
                }

                json_path = os.path.join(self.json_output_dir, f"page_{page_num + 1}.json")
                with open(json_path, 'w') as json_file:
                    json.dump(page_data, json_file, indent=4)

                self.all_pages.append(page_content)

            except Exception as e:
                print(f'Error inside page {page_num + 1}: {e}')

        
        os.remove(self.temp_pdf_path)

        self.all_pages_txt = "\n\n".join(self.all_pages)

        return self.all_pages

    def save_pdf_to_txt(self):
        with open(f'{self.file_output_dir}/{self.file_name}.txt', 'w', encoding='utf-8') as f:
            f.write(self.all_pages_txt)

    def save_pdf_to_pkl(self):
        with open(f'{self.file_output_dir}/{self.file_name}.pkl', 'wb') as f:
            pickle.dump(self.all_pages, f)


    def load_txt(self):
        with open(f'{self.file_output_dir}/{self.file_name}.txt', 'r', encoding='utf-8') as f:
            self.all_pages_txt = f.read()

    


    def clean_text(self, short_line_length=3, exclude_keywords=None, exclude_regex=None, avoid_splitting = 15):
        """
        Cleans and segments the input self.all_pages_txt by removing unwanted characters, lines, and specific content.
        
        Parameters:
        - self.all_pages_txt (str): The self.all_pages_txt to clean and segment.
        - short_line_length (int): Minimum line length to retain. Lines with fewer characters will be removed.
        - exclude_keywords (list of str, optional): List of keywords (e.g., 'Figure', 'Table') that, if found at the beginning of a line, will exclude that line.
        - exclude_regex (str, optional): A custom regular expression pattern. Lines that match this pattern will be removed.
        
        Returns:
        - str: The cleaned and filtered self.all_pages_clean_txt.
        """
        
        self.all_pages_clean_txt = unicodedata.normalize('NFKD', self.all_pages_txt).encode('ASCII', 'ignore').decode('ASCII') # Normalize unicode characters and remove non-ASCII characters
        self.all_pages_clean_txt = self.all_pages_clean_txt.lower()

        self.all_pages_clean_txt = re.sub(r'^\s*-{2,}\s*page\s*\d+\s*-{2,}\s*$', '', self.all_pages_clean_txt, flags=re.IGNORECASE | re.MULTILINE).strip() # Remove page markers
        self.all_pages_clean_txt = re.sub(r'http\S+|www\S+', '', self.all_pages_clean_txt) # Remove URLs
        self.all_pages_clean_txt = re.sub(r'<[^>]*>', '', self.all_pages_clean_txt) # Remove HTML tags
        
        self.all_pages_clean_txt = re.sub(r'[^\x00-\x7F]+', '', self.all_pages_clean_txt) # Remove non-ASCII characters
        self.all_pages_clean_txt = self.all_pages_clean_txt.replace('“', '"').replace('”', '"').replace('’', "'") # Replace non-standard quotes with standard quotes
    

        # Remove hyphenation at line breaks (e.g., "individu-\nals" → "individuals")
        self.all_pages_clean_txt = re.sub(r'-\n', '', self.all_pages_clean_txt)


        # Split the self.all_pages_clean_txt into individual lines
        lines = self.all_pages_clean_txt.splitlines()

        # Filter out lines that don't meet the conditions
        filtered_lines = []
        for line in lines:
            # Exclude lines with just one character (or below the short_line_length threshold)
            if len(line.strip()) <= short_line_length:
                continue
            
            # Exclude lines starting with keywords like 'Figure' or 'Table' (if specified)
            if exclude_keywords:
                if any(line.lower().startswith(keyword.lower()) for keyword in exclude_keywords):
                    continue
            
            # Exclude lines matching the custom regular expression pattern (if specified)
            if exclude_regex:
                if re.match(exclude_regex, line):
                    continue
            
            # If the line passed all filters, keep it
            filtered_lines.append(line)
        
        # Join the remaining lines back into a single self.all_pages_clean_txt block
        self.all_pages_clean_txt = "\n".join(filtered_lines)
        
        
        return self.all_pages_clean_txt


    def save_clean_text(self):
        with open(self.txt_output_processed_path, 'w', encoding='utf-8') as f:
            f.write(self.all_pages_clean_txt)

    def load_clean_text(self):
        with open(self.txt_output_processed_path, 'r', encoding='utf-8') as f:
            self.all_pages_clean_txt = f.read()

    def split_text_into_chunks(self, text, organisation="openai", model_name="gpt-4.1-mini", ):
        """
        Splits cleaned text into semantic chunks using an OpenAI-based semantic chunker.

        Args:
            text (str): The input text to be chunked.

        Returns:
            dict: A dictionary of chunked text segments.
        """
        embedding_function = embedding_functions.OpenAIEmbeddingFunction(api_key=self.openai_api_key, model_name="text-embedding-3-large")

        llm_chunker = LLMSemanticChunker(
            organisation=organisation, 
            model_name=model_name, 
            api_key=self.openai_api_key
        )

        chunks = llm_chunker.split_text(text)

        dct = {}
        for idx, chunk in enumerate(chunks):
            dct[f'chunk_{idx}'] = chunk
        
        self.raw_chunks = dct
        return dct

    def save_raw_chunks(self):
        with open(self.chunk_json_output_path, 'w', encoding='utf-8') as f:
            json.dump(self.raw_chunks, f, indent=4)

    def load_raw_chunks(self):
        with open(self.chunk_json_output_path, 'r', encoding='utf-8') as f:
            self.raw_chunks = json.load(f)



    def __summarize_text(self, text, model):
        """
        Uses an OpenAI model to format and improve a chunk of text.

        Args:
            text (str): The input chunk to clean.
            model (ChatOpenAI): The OpenAI model instance.

        Returns:
            Any: The formatted model output (usually a string).
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert text editor tasked with cleaning and improving text extracted from PDFs. "
                    "Your goal is to fix formatting issues (such as incorrect line breaks, unwanted hyphenation, and improper spacing), "
                    "eliminate redundancy, simplify overly complex sentences, and ensure grammatical correctness. "
                    "Use clear, formal, and active language while preserving the original meaning. Your output should be well-organized and concise."
                )
            },
            {
                "role": "user",
                "content": f"Please clean and format the following text:\n\n{text}"
            }
        ]
        return model.invoke(messages)

    def format_chunks(self, model_name="gpt-4.1-nano"):
        """
        Formats all raw chunks using a GPT model to improve readability and structure.

        Returns:
            dict: A dictionary of formatted text chunks.
        """
        model = ChatOpenAI(model_name=model_name, api_key=self.openai_api_key)

        formatted_chunks = {}

        for key, value in tqdm(self.raw_chunks.items()):
            try:
                formatted_chunks[key] = self.__summarize_text(value, model).content
            except Exception as e:
                print(f"[ERROR] Failed to process chunk {key}: {e}")
                
        self.formatted_chunks = formatted_chunks
        return formatted_chunks

    def save_format_chunks(self):
        with open(self.chunk_json_formatted_output_path, 'w', encoding='utf-8') as f:
            json.dump(self.formatted_chunks, f, indent=4)

    def load_format_chunks(self):
        with open(self.chunk_json_formatted_output_path, 'r', encoding='utf-8') as f:
            self.formatted_chunks = json.load(f)

    def chunks_to_vectorstore(self):
        docs = []
        for idx, chunk in enumerate(self.formatted_chunks.values()):
            doc = Document(
                page_content=chunk,
                metadata = {
                    'origin_title': self.file_name,
                    'chunk_number': idx,
                    'origin_type': self.origin_type
                }
            )
            docs.append(doc)

        self.vectorstore = FAISS.from_documents(docs, self.embeddings)


    def save_vectorestore(self):    
        self.vectorstore.save_local(self.vec_output_path)


    def load_vectorestore(self):
        self.vectorstore = FAISS.load_local(
            self.vec_output_path, self.embeddings, allow_dangerous_deserialization=True
        )

        


def main():

    file_name = 'dr_bernstein_diabetes_solution'
    pp = ProcessPDF(file_name)

    pp.extract_pdf_to_text()
    pp.save_pdf_to_txt()

    pp.load_txt()
    pp.clean_text()
    pp.save_clean_text()

    pp.load_clean_text()
    pp.split_text_into_chunks(pp.all_pages_clean_txt)
    pp.save_raw_chunks()

    pp.load_raw_chunks()
    pp.format_chunks()
    pp.save_format_chunks()

    pp.load_format_chunks()
    pp.chunks_to_vectorstore()
    pp.save_vectorestore()

    pp.load_vectorestore()