from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

from app.core.base.schema import BaseResponseModel


class AttemptBaseData(BaseModel):
    id: str
    test_id: str
    student_id: str
    score: Optional[int]
    max_score: int
    status: str
    started_at: datetime
    expires_at: datetime
    completed_at: Optional[datetime]

class AttemptOptionData(BaseModel):
    id: str
    option_text: str


class AttemptQuestionData(BaseModel):
    id: str
    question_text: str
    options: List[AttemptOptionData]


class FullAttemptData(AttemptBaseData):
    questions: List[AttemptQuestionData]

# attempt response schema
class AttemptResponseModel(BaseResponseModel):
    data: FullAttemptData