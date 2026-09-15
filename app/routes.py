from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.pdf_processor import process_pdf

router = APIRouter()

# Store the chatbot conversation chains
chatbot = None
chatbot_deepseek = None

# Interfaces
class ProcessPDFRequest(BaseModel):
    pdf_url: str

class ChatRequest(BaseModel):
    user_question: str

class ChatTestRequest(BaseModel):
    user_input: str

# Document processing endpoint
@router.post("/process-pdf/")
async def process_pdf_endpoint(request: ProcessPDFRequest):
    global chatbot, chatbot_deepseek

    try:
        questions, summary, chatbot_instance, chatbot_deepseek_instance = process_pdf(request.pdf_url)
        chatbot = chatbot_instance
        chatbot_deepseek = chatbot_deepseek_instance

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

# Chatbot endpoint backed by DeepSeek instead of OpenAI, over the same
# document context (RAG chain built in process_pdf). Matches the frontend's
# existing /chat-test/ contract (user_input -> response).
#
# NOTE on <think> reasoning: the frontend already strips a leading
# <think>...</think> block from the response text (left over from an
# earlier self-hosted DeepSeek-R1 integration, where the model emits
# reasoning inline as part of its raw text output). DeepSeek's *hosted* API
# used here does not do that — it returns reasoning in a separate
# `reasoning_content` field rather than inline text. LangChain's
# ConversationalRetrievalChain abstracts away the raw provider response
# (it saves a plain answer string to memory), so reliably recovering
# reasoning_content through this chain type needs verification against a
# real API key, which isn't available yet. Shipping without it for now is
# safe: the frontend's strip-regex is a no-op when there's no <think> block,
# so the response just renders without a reasoning section until this is
# revisited.
@router.post("/chat-test/")
async def chat_test_endpoint(request: ChatTestRequest):
    global chatbot_deepseek

    if not chatbot_deepseek:
        raise HTTPException(status_code=400, detail="Chatbot not initialized. Process a PDF first.")

    try:
        response = chatbot_deepseek( {"question": request.user_input} )

        return {"response": response["answer"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in chat interaction: {str(e)}")
