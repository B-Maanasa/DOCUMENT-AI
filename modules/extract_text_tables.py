#Extract_text_tables.py
# Importing necessary libraries
import os
import pickle
import pdfplumber
import re

# There's unicode hindering from giving the outputs to the prompts. So, to clean the text, re is used to strip uneccessary data.

def clean_text(text):
    """Clean text to remove invisible/ambiguous unicode characters."""
    text = text.replace("\xa0", " ")  # Non-breaking space
    text = re.sub(r"\s+", " ", text)  # Collapses whitespace
    text = text.strip()
    return text

#

def process_pdfs(pdf_folder, text_output_dir, table_output_dir, chunks_file):

    all_chunks = [] # Collects the data in the form of list.

    for pdf_file in os.listdir(pdf_folder):
        pdf_path = os.path.join(pdf_folder, pdf_file)

        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                # --- Extracting the text --- #
                text = page.extract_text() or ""
                text = clean_text(text)
                if text:
                    chunk = {
                        "type": "text",
                        "content": text,
                        "pdf_source": pdf_file,
                        "page": i
                    }
                    all_chunks.append(chunk)

                # --- Extract tables --- #
                tables = page.extract_tables()
                for table in tables:
                    table_text = "\n".join([" | ".join(map(str, row)) for row in table])
                    table_text = clean_text(table_text)
                    if table_text:
                        chunk = {
                            "type": "table",
                            "content": table_text,
                            "pdf_source": pdf_file,
                            "page": i
                        }
                        all_chunks.append(chunk)

    # --- Save chunks --- #
    with open(chunks_file, "wb") as f:
        pickle.dump(all_chunks, f)

    print(f"Extracted {len(all_chunks)} text/table chunks from PDFs.")
    return all_chunks

def load_chunks(chunks_file):
    with open(chunks_file, "rb") as f:
        chunks = pickle.load(f)
    # Clean again when loading just in case
    for c in chunks:
        c["content"] = clean_text(c["content"])
    return chunks
