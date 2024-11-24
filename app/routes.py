from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.pdf_processor import process_pdf

router = APIRouter()

# Store the chatbot conversation chain
chatbot = None

# Interfaces
class ProcessPDFRequest(BaseModel):
    pdf_url: str

class ChatRequest(BaseModel):
    user_question: str

# Document processing endpoint
@router.post("/process-pdf/")
async def process_pdf_endpoint(request: ProcessPDFRequest):
    global chatbot

    try:
        questions, summary, chatbot_instance = process_pdf(request.pdf_url)
        chatbot = chatbot_instance

        return {"questions": questions, "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

# Chatbot endpoint
@router.post("/chat/")
async def chat_endpoint(request: ChatRequest):
    global chatbot

    if not chatbot:
        raise HTTPException(status_code=400, detail="Chatbot not initialized. Process a PDF first.")
    
    try:
        response = chatbot( {"question": request.user_question} )
        
        return {"bot_response": response["answer"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in chat interaction: {str(e)}")