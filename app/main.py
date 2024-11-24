from fastapi import FastAPI
from app.routes import router

app = FastAPI(
    title="Hero AI Backend",
    description="Backend API for document processing, generation of multiple choice questions, and chatbot interaction.",
    version="1.0.0"
)

# Routes
app.include_router(router)