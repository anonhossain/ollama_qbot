from fastapi import FastAPI
from views import api

app = FastAPI(
    title="Ollama Question Simulator", 
    description="This is a question simulation app powered by Ollama.",
    version="1.0.0",       
              )
app.include_router(api)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="localhost",  # Use localhost for pc or 0.0.0.0 for Docker
        port=8080,
        reload=True
    )