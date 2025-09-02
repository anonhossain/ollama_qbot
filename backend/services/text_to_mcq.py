import os
import json
from dotenv import load_dotenv
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings  # Correct import for the latest version
from ollama import Client

# Load environment variables from .env file
load_dotenv()

# Fetch environment variables
ollama_host_url = os.getenv("OLLAMA_HOST_URL")
embedding_model = os.getenv("EMBEDDING_MODEL")
mcq_model = os.getenv("MCQ_MODEL")

# Debugging: Print the loaded environment variables to check
# print(f"OLLAMA_HOST_URL: {ollama_host_url}")
# print(f"EMBEDDING_MODEL: {embedding_model}")
# print(f"MCQ_MODEL: {mcq_model}")

# Validate the variables to make sure they are not None or empty
if not ollama_host_url or not embedding_model:
    raise ValueError("OLLAMA_HOST_URL and EMBEDDING_MODEL must be set in the environment variables.")

# --- Setup ---
client = Client(host=ollama_host_url)
embeddings = OllamaEmbeddings(model=embedding_model, base_url=ollama_host_url)


class TextToMCQ:
    """Convert cleaned text into MCQs using Chroma DB and Ollama API."""

    def __init__(self, text: str, output_folder: str = "output"):
        self.text = text
        self.output_folder = output_folder

    def load_and_clean_text(self):
        """Clean the input text and prepare for processing."""
        lines = [line for line in self.text.splitlines() if not line.strip().startswith('--- Page')]
        cleaned_text = "\n".join(lines)
        return cleaned_text

    def embed_text_to_db(self, text, persist_dir="./qwen_embed", collection_name="local_rag_db"):
        """Embed cleaned text into Chroma DB."""
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

    def generate_raw_mcqs(self, vector_db, num_questions, output_file="mcqs_raw.json"):
        """Generate raw MCQs based on the content in Chroma DB."""
        docs = vector_db._collection.get(include=["documents"])["documents"]
        if not docs:
            print("⚠️ No documents found in DB.")
            return

        raw_prompt_template = """
        Based on the following content, generate ONE multiple-choice question.
        Important Instructions:
            - Follow the format STRICTLY as shown below.
            - Do NOT use raw examples mentioned in the text directly as answer options, unless they are essential for understanding.
            - The question must be clear, contextual, and stand alone (it should make sense even without reading the original text).
            - Keep the description concise and explanatory.

        Question No: <number>
        Question: <the question>
        Options:
        A. <option A>
        B. <option B>
        C. <option C>
        D. <option D>
        Correct Answer: Just Correct Option (A or B or C or D)
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

        # Save generated MCQs in JSON format
        os.makedirs(self.output_folder, exist_ok=True)
        with open(os.path.join(self.output_folder, output_file), "w", encoding="utf-8") as f:
            json.dump(raw_mcqs, f, indent=4)

        print(f"💾 Saved raw MCQs to {os.path.join(self.output_folder, output_file)}")

    def process(self, num_questions=10):
        """Full process to clean text, embed it into the database, and generate MCQs."""
        cleaned_text = self.load_and_clean_text()
        db = self.embed_text_to_db(cleaned_text)
        self.generate_raw_mcqs(db, num_questions)


# --- Running the pipeline ---
if __name__ == "__main__":
    # Assuming text extraction from PDF has been done and you now have `cleaned_text`
    # cleaned_text = "Extracted text from PDF"
    txt_file_path = "output/combined_output.txt"  # Path to the text file that you got from pdf_to_text.py
    
    with open(txt_file_path, "r", encoding="utf-8") as f:
        extracted_text = f.read()

    # Create an instance of the TextToMCQ class and run the process
    text_to_mcq_processor = TextToMCQ(extracted_text, output_folder="output")
    text_to_mcq_processor.process(num_questions=10)
