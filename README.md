# Ollama Chatbot Repository

This repository is set up for working with the **Ollama chatbot** using an embedding model and a large language model (LLM). Follow the instructions below to install, configure, and run the chatbot.

## Prerequisites

Before running the Ollama chatbot, ensure you have the following prerequisites installed:

- **Ollama**: Make sure to install Ollama on your system. You can download it from [Ollama's official website](https://ollama.com/).
- **Python**: This repository uses Python, so ensure Python 3.7 or higher is installed.

## Setup Instructions

### 1. Clone the Repository

Clone this repository to your local machine:

```bash
git clone anonhossain/ollama_qbot
cd <your-repository-directory>
```
## Install Ollama
```
ollama install

```

## Pull the Embedding Model
```
ollama pull nomic-embed-text
```
## Pull the LLM Model
```
ollama pull llama3.1:8b
```
## Create the Necessary Folders

## Create .env and put the credentials:

```
# Embedding Model Configuration
EMBEDDING_MODEL = 'nomic-embed-text'   # Replace with your embedding model name

# Ollama Host URL
OLLAMA_HOST_URL = "http://localhost:11434"

# Language Model Configuration
OLLAMA_MODEL = "llama3.1:8b"  # Replace with your LLM model name (e.g., llama3.1:8b)

# Chroma Configuration
PERSIST_DIRECTORY = "./chroma_db"
CHROMA_COLLECTION_NAME = "collection_name"  # Replace with your preferred collection name
```
Install Required Python Packages

```
pip install -r requirements.txt
```
