from PyPDF2 import PdfReader, PdfWriter

# Open the original PDF
reader = PdfReader("s/standards-of-care-2025.pdf")

# Create a new PDF writer
writer = PdfWriter()

# Add page 20 (index 19)
writer.add_page(reader.pages[19])

# Get the 20th page (index 19)
page20 = reader.pages[19]

# Extract text
text = page20.extract_text()

print(text)

# Save it to a new PDF
with open("page_20_output.pdf", "wb") as f:
    writer.write(f)

print("Saved page 20 to 'page_20_output.pdf'")
