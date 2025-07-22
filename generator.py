# import json
# import os
# from dotenv import load_dotenv
# from langchain_community.embeddings import OllamaEmbeddings
# from langchain_community.vectorstores import Chroma
# from ollama import Client

# load_dotenv()

# OLLAMA_HOST_URL = os.getenv("OLLAMA_HOST_URL")
# EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
# PERSIST_DIRECTORY = os.getenv("PERSIST_DIRECTORY")
# CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME")
# OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

# # Setup Ollama client
# ollama_host_url = OLLAMA_HOST_URL
# client = Client(host=ollama_host_url)

# # Load the Chroma vector database and use the same embedding model
# embedding_model = EMBEDDING_MODEL
# vector_db = Chroma(persist_directory=PERSIST_DIRECTORY, 
#                    embedding_function=OllamaEmbeddings(model=embedding_model, 
#                                                        base_url=ollama_host_url, 
#                                                        show_progress=True), 
#                                                        collection_name=CHROMA_COLLECTION_NAME
#                                                        )

# # Function to generate MCQ from the chunk of text
# def generate_mcq_from_text(text):
#     """Generate MCQ from provided text using Ollama model."""
#     prompt = f"""
#     Generate a multiple-choice question (MCQ) from the following text. The MCQ should include:
#     - A question
#     - Four options (a, b, c, d)
#     - The correct option
#     - A description

#     Text:
#     {text}

#     Please return the output in the following JSON format:
#     {{
#         "question": "<question>",
#         "options": [
#             {{ "option_a": "<option_1>" }},
#             {{ "option_b": "<option_2>" }},
#             {{ "option_c": "<option_3>" }},
#             {{ "option_d": "<option_4>" }}
#         ],
#         "correct_option": "<correct_option>",
#         "description": "<description>"
#     }}
#     """

#     # Send the prompt to Ollama
#     response = client.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])

#     # Check if the response contains the expected message
#     if 'message' not in response or 'content' not in response['message']:
#         print("Error: Response does not contain the expected content.")
#         return None

#     # Print the raw response to inspect it
#     print("Response from Ollama:", response['message']['content'])

#     # Get the generated MCQ
#     return response['message']['content']

# # Function to generate MCQs for documents from the Chroma database
# def generate_mcqs_from_chroma():
#     # Use the Chroma vector store to fetch documents based on similarity
#     retriever = vector_db.as_retriever()
#     question = "Generate MCQs from this content."

#     # Retrieve documents (chunks) from Chroma
#     docs = retriever.invoke(question)
#     print("Documents fetched from database: ", len(docs))

#     mcqs = []

#     # For each document chunk, generate MCQs
#     for doc in docs:
#         text = doc.page_content
#         mcq_json = generate_mcq_from_text(text)
        
#         if mcq_json:  # Only proceed if the MCQ was successfully generated
#             try:
#                 mcqs.append(json.loads(mcq_json))  # Convert the generated MCQ to a JSON object
#             except json.JSONDecodeError:
#                 print(f"Error parsing MCQ for document {doc.id}")
#                 continue  # Skip this document if parsing fails

#     # Optionally, save the MCQs to a file
#     with open("generated_mcqs.json", "w") as f:
#         json.dump(mcqs, f, indent=4)

#     return mcqs

# # Example usage
# mcqs = generate_mcqs_from_chroma()
# print("Generated MCQs:", mcqs)




# import json
# import os
# from dotenv import load_dotenv
# from langchain_ollama import OllamaEmbeddings
# from langchain_chroma import Chroma
# from ollama import Client

# load_dotenv()

# OLLAMA_HOST_URL = os.getenv("OLLAMA_HOST_URL")
# EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
# PERSIST_DIRECTORY = os.getenv("PERSIST_DIRECTORY")
# CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME")
# OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

# # Setup Ollama client
# ollama_host_url = OLLAMA_HOST_URL
# client = Client(host=ollama_host_url)

# # Load the Chroma vector database and use the same embedding model
# embedding_model = EMBEDDING_MODEL
# vector_db = Chroma(persist_directory=PERSIST_DIRECTORY, 
#                    embedding_function=OllamaEmbeddings(model=embedding_model, 
#                                                        base_url=ollama_host_url),  # Removed show_progress
#                    collection_name=CHROMA_COLLECTION_NAME
#                    )

# # Number of MCQs to generate
# generate_mcq = 10  # Set this to the number of MCQs you want to generate

# # Function to generate MCQ from the chunk of text
# def generate_mcq_from_text(text):
#     """Generate MCQ from provided text using Ollama model."""
#     prompt = f"""
#     Generate a multiple-choice question (MCQ) from the following text. The MCQ should include:
#     - A question
#     - Four options (a, b, c, d)
#     - The correct option
#     - A description

#     Text:
#     {text}

#     Please return the output in the following JSON format:
#     {{
#         "question": "<question>",
#         "options": [
#             {{ "option_a": "<option_1>" }},
#             {{ "option_b": "<option_2>" }},
#             {{ "option_c": "<option_3>" }},
#             {{ "option_d": "<option_4>" }}
#         ],
#         "correct_option": "<correct_option>",
#         "description": "<description>"
#     }}
#     """

#     # Send the prompt to Ollama
#     response = client.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])

#     # Check if the response contains the expected message
#     if 'message' not in response or 'content' not in response['message']:
#         print("Error: Response does not contain the expected content.")
#         return None

#     # Get the generated MCQ
#     mcq_content = response['message']['content']

#     # Check if the MCQ content is empty or invalid
#     if not mcq_content:
#         print(f"Error: Empty MCQ content generated for text: {text}")
#         return None

#     # Clean up the response to remove extra spaces or invalid characters before parsing
#     mcq_content = mcq_content.strip()  # Strip leading/trailing whitespace

#     # Attempt to load the MCQ response as JSON
#     try:
#         mcq_json = json.loads(mcq_content)
#     except json.JSONDecodeError as e:
#         print(f"Error parsing MCQ response: {e}")
#         print(f"Invalid MCQ content: {mcq_content}")
#         return None

#     return mcq_json

# # Function to generate MCQs for documents from the Chroma database
# def generate_mcqs_from_chroma():
#     # Use the Chroma vector store to fetch documents based on similarity
#     retriever = vector_db.as_retriever()
#     question = "Generate MCQs from this content."

#     # Retrieve documents (chunks) from Chroma
#     docs = retriever.invoke(question)
#     print(f"Documents fetched from database: {len(docs)}")  # Debugging message to check number of documents

#     mcqs = []
#     questions_generated = 0  # Track how many MCQs have been generated

#     # Loop to generate multiple questions from the same documents
#     while questions_generated < generate_mcq:
#         # Loop over the documents to generate MCQs
#         for doc in docs:
#             if questions_generated >= generate_mcq:
#                 break  # Stop once the required number of questions is reached

#             print(f"Processing document {doc.id}")  # Debugging message to check document ID being processed
#             text = doc.page_content
#             mcq_json = generate_mcq_from_text(text)

#             if mcq_json:  # Only proceed if the MCQ was successfully generated
#                 mcqs.append(mcq_json)
#                 questions_generated += 1
#                 print(f"MCQ generated for document {doc.id}: {mcq_json['question']}")  # Debugging message to print the MCQ question

#         # Optional: If you want to generate more MCQs even if you exhaust all documents,
#         # you can repeat the loop for more MCQs by fetching new documents, etc.
#         if questions_generated < generate_mcq:
#             print("Restarting question generation as needed...")  # Debugging message

#     # Return the list of MCQs
#     return mcqs

# # Example usage
# mcqs = generate_mcqs_from_chroma()

# # Print only the MCQ questions
# if mcqs:
#     for mcq in mcqs:
#         print(f"Question: {mcq['question']}")
# else:
#     print("No MCQs generated.")


import json
import os
import random
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from ollama import Client

load_dotenv()

OLLAMA_HOST_URL = os.getenv("OLLAMA_HOST_URL")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
PERSIST_DIRECTORY = os.getenv("PERSIST_DIRECTORY")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

# Setup Ollama client
ollama_host_url = OLLAMA_HOST_URL
client = Client(host=ollama_host_url)

# Load the Chroma vector database and use the same embedding model
embedding_model = EMBEDDING_MODEL
vector_db = Chroma(persist_directory=PERSIST_DIRECTORY, 
                   embedding_function=OllamaEmbeddings(model=embedding_model, 
                                                       base_url=ollama_host_url),
                   collection_name=CHROMA_COLLECTION_NAME)

# Number of MCQs to generate
generate_mcq = 6
  # Set this to the number of MCQs you want to generate
questions_generated = 0  # Initialize question counter
mcqs = []  # List to store generated MCQs

# Function to generate MCQ from the chunk of text
def generate_mcq_from_text(text):
    """Generate MCQ from provided text using Ollama model."""
    prompt = f"""
    Generate a multiple-choice question (MCQ) from the following text. The MCQ should include:
    - A question
    - Four options (a, b, c, d)
    - The correct option
    - A description

    Text:
    {text}

    Please return the output in the following JSON format:
    {{
        "question": "<question>",
        "options": [
            {{ "option_a": "<option_1>" }},
            {{ "option_b": "<option_2>" }},
            {{ "option_c": "<option_3>" }},
            {{ "option_d": "<option_4>" }}
        ],
        "correct_option": "<correct_option>",
        "description": "<description>"
    }}
    """

    # Send the prompt to Ollama
    response = client.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])

    # Check if the response contains the expected message
    if 'message' not in response or 'content' not in response['message']:
        print("Error: Response does not contain the expected content.")
        return None

    # Get the generated MCQ
    mcq_content = response['message']['content']

    # Check if the MCQ content is empty or invalid
    if not mcq_content:
        print(f"Error: Empty MCQ content generated for text: {text}")
        return None

    # Clean up the response to remove extra spaces or invalid characters before parsing
    mcq_content = mcq_content.strip()  # Strip leading/trailing whitespace

    # Attempt to load the MCQ response as JSON
    try:
        mcq_json = json.loads(mcq_content)
    except json.JSONDecodeError as e:
        print(f"Error parsing MCQ response: {e}")
        print(f"Invalid MCQ content: {mcq_content}")
        return None

    return mcq_json

def generate_mcqs_from_chroma():
    # Use the Chroma vector store to fetch documents based on similarity
    retriever = vector_db.as_retriever()
    question = "Generate MCQs from this content."

    # Retrieve documents (chunks) from Chroma
    docs = retriever.invoke(question)
    print(f"Documents fetched from database: {len(docs)}")  # Debugging message to check number of documents

    mcqs = []
    questions_generated = 0  # Track how many MCQs have been generated

    # Loop through the number of questions to generate
    while questions_generated < generate_mcq:
        print(f"Total questions generated so far: {questions_generated}")  # Debugging message to track progress
        questions_generated += 1
        # Randomly select one document each time
        selected_doc = random.choice(docs)

        # Process the selected document and generate one MCQ
        print(f"Processing document {selected_doc.id}")  # Debugging message to check document ID being processed
        text = selected_doc.page_content
        mcq_json = generate_mcq_from_text(text)

        if mcq_json:  # Only proceed if the MCQ was successfully generated
            mcqs.append(mcq_json)
            

            # Print the generated MCQ question and update the question counter
            print(f"MCQ generated: {mcq_json['question']}")  # Debugging message to print the MCQ question
            print(f"Generated Question: {questions_generated}")
            print(f"Question: {mcq_json['question']}")

            # Optionally save each MCQ to a JSON file after generating each one
            with open('generated_mcq.json', 'a') as f:
                json.dump(mcq_json, f, ensure_ascii=False, indent=4)
                f.write("\n")

        # Print status if there are remaining MCQs to be generated
        if questions_generated < generate_mcq:
            print(f"Continuing to next document... Total generated: {questions_generated}")

    # Return the list of MCQs
    return mcqs

# Example usage
mcqs = generate_mcqs_from_chroma()

# Print only the MCQ questions
if mcqs:
    for mcq in mcqs:
        print(f"Question: {mcq['question']}")
else:
    print("No MCQs generated.")



