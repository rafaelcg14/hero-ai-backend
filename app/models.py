from pydantic import BaseModel
from typing import List, Optional, Dict

class MCQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str
    topic: str

class QuestionResponse(BaseModel):
    question_id: str
    chunk_id: str
    question_dict: MCQuestion
    reference_page: Optional[int]