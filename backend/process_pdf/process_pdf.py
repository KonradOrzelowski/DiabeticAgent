import os

class ProcessPDF:
    def __init__(self, file_name):
        self.file_name = file_name

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

        self.all_pages = None
        self.all_pages_txt = None
        self.all_pages_clean_txt = None


    def extract_pdf_to_text(self):
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
        # Normalize unicode characters and remove non-ASCII characters
        self.all_pages_clean_txt = unicodedata.normalize('NFKD', self.all_pages_txt).encode('ASCII', 'ignore').decode('ASCII')
        
        # Convert all characters to lowercase for uniformity
        self.all_pages_clean_txt = self.all_pages_clean_txt.lower()

        # Remove page markers and URLs
        self.all_pages_clean_txt = re.sub(r'^\s*-{2,}\s*page\s*\d+\s*-{2,}\s*$', '', self.all_pages_clean_txt, flags=re.IGNORECASE | re.MULTILINE).strip()
        self.all_pages_clean_txt = re.sub(r'http\S+|www\S+', '', self.all_pages_clean_txt)
        
        # Remove HTML tags
        self.all_pages_clean_txt = re.sub(r'<[^>]*>', '', self.all_pages_clean_txt)
        
        # Remove non-ASCII characters that weren't already removed by normalization
        self.all_pages_clean_txt = re.sub(r'[^\x00-\x7F]+', '', self.all_pages_clean_txt)
        
        # Replace non-standard quotes with standard quotes
        self.all_pages_clean_txt = self.all_pages_clean_txt.replace('“', '"').replace('”', '"').replace('’', "'")
        
        # Trim leading and trailing spaces
        self.all_pages_clean_txt = self.all_pages_clean_txt.strip()

        # Remove hyphenation at line breaks (e.g., "individu-\nals" → "individuals")
        self.all_pages_clean_txt = re.sub(r'-\n', '', self.all_pages_clean_txt)

        # Replace remaining newlines with space (optional, for paragraph formatting)
        self.all_pages_clean_txt = self.all_pages_clean_txt.replace('\n', ' ')

        # Clean up parentheses and extra spaces
        self.all_pages_clean_txt = re.sub(r"\([^()]*\)", "", self.all_pages_clean_txt)
        self.all_pages_clean_txt = re.sub(r"\s{2,}", " ", self.all_pages_clean_txt).strip()

        # Split joined words (like "atpresentation" → "at presentation")
        words = []
        for word in self.all_pages_clean_txt.split():
            if len(word) > avoid_splitting:  # Heuristic to avoid splitting short normal words
                words.extend(wordninja.split(word))
            else:
                words.append(word)
        
        self.all_pages_clean_txt = " ".join(words)

        # Step 1: Split the self.all_pages_clean_txt into individual lines
        lines = self.all_pages_clean_txt.splitlines()

        # Step 2: Filter out lines that don't meet the conditions
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
        pass

    def split_text_into_chunks(self):
        pass

    def save_raw_chunks(self):
        pass

    def format_chunks(self):
        pass

    def save_format_chunks(self):
        pass
