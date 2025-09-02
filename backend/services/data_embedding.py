# import section
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.document_loaders import OnlinePDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.embeddings import OllamaEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import fitz  # PyMuPDF

load_dotenv()

EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL')
PERSIST_DIRECTORY = os.getenv('PERSIST_DIRECTORY')
OLLAMA_COLLECTION_NAME = os.getenv('CHROMA_COLLECTION_NAME')

# Define the path to the PDF file
file_path_local = 'file/Data.pdf'

# Open the PDF
doc = fitz.open(file_path_local)

# Extract text from all pages
pdf_text = ""
for page_num in range(doc.page_count):
    page = doc.load_page(page_num)
    pdf_text += page.get_text()

# Print the extracted text
# print(pdf_text)

# Create a Document object to hold the text content
document = Document(page_content=pdf_text)

# Set up the RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)

# Split the document into chunks
data_chunks = text_splitter.split_documents([document])

# Print the results
print("Data chunks created....")
for chunk in data_chunks:
    print(chunk.page_content)

# Use the correct model name
embedding = OllamaEmbeddings(model=EMBEDDING_MODEL, show_progress=True)

# Store chunks and embeddings in Chroma
Chroma.from_documents(data_chunks, embedding, persist_directory=PERSIST_DIRECTORY, collection_name=OLLAMA_COLLECTION_NAME)
