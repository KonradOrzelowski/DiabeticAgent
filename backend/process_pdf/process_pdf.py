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

        return self.all_pages

    def save_pdf_to_txt(self):
        with open(f'{self.file_output_dir}/{self.file_name}.txt', 'w', encoding='utf-8') as f:
            f.write("\n\n".join(self.all_pages))

    def save_pdf_to_pkl(self):
        with open(f'{self.file_output_dir}/{self.file_name}.pkl', 'wb') as f:
            pickle.dump(self.all_pages, f)

    def clean_text(self):
        pass

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
