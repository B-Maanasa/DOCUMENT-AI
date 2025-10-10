# main.py

import os
from modules.extract_text_tables import process_pdfs
from modules.extract_images_charts import process_pdfs_images_charts
from modules.embed_retrieve import EmbedRetrieve

# --- Folders --- #
PDF_FOLDER = "data"
TEXT_OUTPUT_DIR = "outputs/text_chunks"
TABLE_OUTPUT_DIR = "outputs/table_chunks"
IMAGE_OUTPUT_DIR = "outputs/image_chunks"
CHART_OUTPUT_DIR = "outputs/chart_chunks"

# --- Chunks files --- #
TEXT_TABLE_CHUNKS_FILE = "outputs/chunks_text_table.pkl"
IMAGE_CHART_CHUNKS_FILE = "outputs/chunks_image_chart.pkl"

# --- FAISS index --- #
FAISS_INDEX_FILE = "outputs/faiss_index.idx"

# ---  Processes PDFs --- #
print("Processing text and tables...")
text_table_chunks = process_pdfs(PDF_FOLDER, TEXT_OUTPUT_DIR, TABLE_OUTPUT_DIR, TEXT_TABLE_CHUNKS_FILE)

print("Processing images and charts...")
image_chart_chunks = process_pdfs_images_charts(PDF_FOLDER, IMAGE_OUTPUT_DIR, CHART_OUTPUT_DIR, IMAGE_CHART_CHUNKS_FILE)

# --- Builds embeddings & FAISS index --- #
er = EmbedRetrieve(
    chunks_files=[TEXT_TABLE_CHUNKS_FILE, IMAGE_CHART_CHUNKS_FILE],
    faiss_index_file=FAISS_INDEX_FILE
)

er.load_all_chunks()
er.build_index()

print("All done!")
