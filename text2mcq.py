import os
import json
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from ollama import Client

# --- Setup ---
ollama_host_url = "http://localhost:11434"
embedding_model = "dengcao/Qwen3-Embedding-8B:Q8_0"
mcq_model = "gpt-oss:20b"

client = Client(host=ollama_host_url)
embeddings = OllamaEmbeddings(model=embedding_model, base_url=ollama_host_url, show_progress=True)


# --- Step 1: Load .txt file and clean content ---
def load_and_clean_txt(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        text = f.read()
    lines = [line for line in text.splitlines() if not line.strip().startswith('--- Page')]
    cleaned_text = "\n".join(lines)
    return cleaned_text


# --- Step 2: Embed text into Chroma DB ---
def embed_text_to_db(text, persist_dir="./qwen_embed", collection_name="local_rag_db"):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_text(text)
    docs = [Document(page_content=chunk) for chunk in chunks if chunk.strip()]

    vector_db = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings,
        collection_name=collection_name
    )

    vector_db.add_documents(docs)
    print(f"✅ Embedded {len(docs)} meaningful chunks into Chroma DB")
    return vector_db


# --- Step 3a: Generate MCQs (raw text format) ---
def generate_raw_mcqs(vector_db, num_questions=10, output_file="mcqs_raw.txt"):
    docs = vector_db._collection.get(include=["documents"])["documents"]
    if not docs:
        print("⚠️ No documents found in DB.")
        return

    raw_prompt_template = """
    Based on the following content, generate ONE multiple-choice question.
    Format STRICTLY like this:

    Question No: <number>
    Question: <the question>
    Options:
    A. <option A>
    B. <option B>
    C. <option C>
    D. <option D>
    Correct Answer: <letter>
    Description: <short explanation>

    Content: {content}
    """

    doc_index = 0
    total_docs = len(docs)
    raw_mcqs = []

    while len(raw_mcqs) < num_questions:
        content = docs[doc_index % total_docs]  # cycle through docs
        prompt = raw_prompt_template.format(content=content)

        response = client.chat(model=mcq_model, messages=[{"role": "user", "content": prompt}])
        mcq_text = response.get("message", {}).get("content", "").strip()

        if mcq_text:
            raw_mcqs.append(mcq_text)
            print(f"✅ Generated raw Q{len(raw_mcqs)}")
        else:
            print(f"⚠️ Empty response for doc {doc_index}")

        doc_index += 1

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n\n".join(raw_mcqs))
    print(f"💾 Saved raw MCQs to {output_file}")


# --- Run Pipeline ---
if __name__ == "__main__":
    txt_file = "Notes.txt"
    cleaned_text = load_and_clean_txt(txt_file)

    db = embed_text_to_db(cleaned_text)

    total_questions = 10  # change as needed

    # Step 1: Generate plain-text MCQs
    generate_raw_mcqs(db, num_questions=total_questions, output_file="mcqs_raw.txt")

