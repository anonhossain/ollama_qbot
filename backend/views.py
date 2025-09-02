from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from services.preprocessing import generate_mcqs_pipeline
from file_manager import delete_all_pdfs, save_uploaded_files

api = APIRouter(prefix="/api")

@api.get("/hello", tags=["Greeting"])
def hello():
    return {"message": "Hello, Anon!"}

# Endpoint to upload files
@api.post("/upload-files/", tags=["File Manager"])
async def upload_files(files: list[UploadFile] = File(...)):
    try:
        uploaded_file_names = await save_uploaded_files(files)
        return JSONResponse(
            content={"message": "Files successfully uploaded", "files": uploaded_file_names},
            status_code=200  # OK status code
        )
    except HTTPException as e:
        raise e  # Forward HTTPException to return proper status code
    except Exception as e:
        # Catch any unexpected exceptions and return a 500 error
        raise HTTPException(status_code=500, detail=f"Unexpected error occurred: {str(e)}")


# Endpoint to delete all PDF files
@api.delete("/delete-pdfs/", tags=["File Manager"])
async def delete_pdfs():
    try:
        deleted_files = delete_all_pdfs()
        
        if deleted_files:
            return JSONResponse(
                content={"message": "Successfully deleted PDF files", "files_deleted": deleted_files},
                status_code=200  # OK status code
            )
        else:
            return JSONResponse(
                content={"message": "No PDF files found to delete"},
                status_code=404  # Not Found if no PDFs are deleted
            )
    except Exception as e:
        # Catch any unexpected exceptions and return a 500 error
        raise HTTPException(status_code=500, detail=f"Error occurred while deleting files: {str(e)}")

# API endpoint to generate MCQs from PDFs
@api.post("/generate-mcqs", tags=["File Manager"])
async def generate_mcqs():
    try:
        result = generate_mcqs_pipeline()
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)