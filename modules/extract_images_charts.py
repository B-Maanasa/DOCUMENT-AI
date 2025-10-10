#Extract_images_charts.py

# Importing necessary libraries
import os
import pickle
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import re

# There's unicode hindering from giving the outputs to the prompts. So, to clean the text, re is used to strip uneccessary data.
def clean_text(text):
    """Clean text to remove invisible/ambiguous unicode characters."""
    text = text.replace("\xa0", " ")  # non-breaking space
    text = re.sub(r"\s+", " ", text)  # collapse whitespace
    text = text.strip()
    return text

def process_pdfs_images_charts(pdf_folder, image_output_dir, chart_output_dir, chunks_file):

    all_chunks = []

    for pdf_file in os.listdir(pdf_folder):
        pdf_path = os.path.join(pdf_folder, pdf_file)

        doc = fitz.open(pdf_path)
        for i, page in enumerate(doc, 1):
            # --- Extracting the images ---#
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list, 1):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_name = f"{os.path.splitext(pdf_file)[0]}_page{i}_img{img_index}.{image_ext}"
                image_path = os.path.join(image_output_dir, image_name)
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)

                # OCR text from image (optional, can be empty)
                try:
                    img_obj = Image.open(image_path)
                    ocr_text = pytesseract.image_to_string(img_obj)
                    ocr_text = clean_text(ocr_text)
                except Exception:
                    ocr_text = ""

                chunk = {
                    "type": "image",
                    "content": ocr_text,
                    "pdf_source": pdf_file,
                    "page": i,
                    "image_path": image_path
                }
                all_chunks.append(chunk)

            # --- Extract charts as images (optional) ---
            # For simplicity, we treat charts as images
            # Users can later filter by captions or regions if needed
            # Add chart placeholder chunk
            chart_chunk = {
                "type": "chart",
                "content": f"Chart placeholder on page {i} of {pdf_file}",
                "pdf_source": pdf_file,
                "page": i
            }
            all_chunks.append(chart_chunk)

    # --- Save chunks ---
    with open(chunks_file, "wb") as f:
        pickle.dump(all_chunks, f)

    print(f"Extracted {len(all_chunks)} image/chart chunks from PDFs.")
    return all_chunks

def load_chunks(chunks_file):
    with open(chunks_file, "rb") as f:
        chunks = pickle.load(f)
    # Clean content
    for c in chunks:
        if "content" in c:
            c["content"] = clean_text(c["content"])
    return chunks
