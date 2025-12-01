from datetime import datetime
from pydantic import BaseModel, StringConstraints
from typing import Annotated, List, Optional
from app.core.base.schema import BaseResponseModel, PaginatedResponse

class QuestionBaseData(BaseModel):
    id: str
    question_text: str
    created_at: datetime
    updated_at: datetime

class QuestionOptionBaseData(BaseModel):
    option_text: str
    is_correct: bool

class FullQuestionData(QuestionBaseData):
    options: List[QuestionOptionBaseData]

# question creation schema
class QuestionCreateSchema(BaseModel):
    question_text: Annotated[str, StringConstraints(max_length=500)]
    options: List[QuestionOptionBaseData]

# question bulk creation schema
class QuestionsBulkCreateSchema(BaseModel):
    questions: List[QuestionCreateSchema]

# question update schema
class QuestionUpdateSchema(BaseModel):
    question_text: Optional[Annotated[str, StringConstraints(max_length=500)]] = None
    options: Optional[List[QuestionOptionBaseData]] = None

# question response schema
class QuestionResponseModel(BaseResponseModel):
    data: FullQuestionData

# question bulk creation response schema
class QuestionsBulkCreateResponseModel(BaseResponseModel):
    data: List[FullQuestionData]

# paginated question response schema
class QuestionsPaginatedData(PaginatedResponse):
    """Paginated response model with question items"""

    items: List[FullQuestionData]

class QuestionsListResponseModel(BaseResponseModel):
    data: QuestionsPaginatedData