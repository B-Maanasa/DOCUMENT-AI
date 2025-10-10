# app.py

import streamlit as st
from modules.embed_retrieve import EmbedRetrieve

# --- Constants --- #
FAISS_INDEX_FILE = "outputs/faiss_index.idx"

# --- Loads FAISS index --- #
er = EmbedRetrieve(chunks_files=[], faiss_index_file=FAISS_INDEX_FILE)
er.load_index()

# --- Streamlit UI --- #
st.set_page_config(page_title="Telangana Socio Economic Outlook Chatbot", layout="wide")
st.title("🏦Telangana Socio Economic Outlook Chatbot")

# --- Chat history --- #
if "history" not in st.session_state:
    st.session_state.history = []

# --- User input form (Enter submits) --- #
with st.form(key="chat_form", clear_on_submit=True):
    query = st.text_input("Ask a question:", key="user_input")
    submitted = st.form_submit_button("Send")

if submitted and query:
    # Search top 5 relevant chunks
    results = er.search(query, top_k=5)
    
    # Prepares reply text
    reply_text = ""
    for res in results:
        chunk = res["chunk"]
        distance = res.get("distance", 0)
        content = chunk.get("content", "")
        source = chunk.get("pdf_source", "unknown")
        page = chunk.get("page", "unknown")
        reply_text += f"**Source:** {source}, **Page:** {page}\n{content}\n\n"

    # Update chat history 
    st.session_state.history.append({"query": query, "reply": reply_text})

# --- Display chat history --- #
for chat in st.session_state.history[::-1]:  # shown in reverse chronological order
    st.markdown(f"**Prompt:** {chat['query']}")
    st.markdown(f"**Reply:** {chat['reply']}")
    st.markdown("---")
