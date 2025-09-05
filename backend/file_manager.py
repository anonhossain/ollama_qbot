from fastapi import UploadFile, HTTPException
from pathlib import Path
import os

from grpc import services

# Define the base folder path
BASE_DIR = Path(__file__).parent.parent  # assuming the script is in 'ollama_qbot/backend'
UPLOAD_FOLDER = BASE_DIR / "upload"

# Ensure the upload directory exists
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)  # Creates the folder if it doesn't exist

async def save_uploaded_files(files: list[UploadFile]) -> list[str]:
    uploaded_file_names = []

    # Iterate over all the files received in the request
    for file in files:
        # Check if the file is a PDF
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

        file_location = UPLOAD_FOLDER / file.filename

        # Save the file to the upload folder
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)
        
        uploaded_file_names.append(file.filename)
    
    return uploaded_file_names

# Function to delete all PDF files from the upload folder
def delete_all_pdfs() -> list[str]:
    deleted_files = []
    
    # Iterate over the files in the upload folder
    for file in UPLOAD_FOLDER.iterdir():
        if file.suffix.lower() == ".pdf":  # Check if the file is a PDF
            os.remove(file)  # Delete the file
            deleted_files.append(file.name)  # Add the deleted file's name to the list
    
    return deleted_files
