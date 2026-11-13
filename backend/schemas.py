from datetime import datetime 
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

# Authentication / Users
class UserCreate(BaseModel):
    username: str = Field(min_length=3)
    email: str
    password: str = Field(min_length=6)

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    model_config = ConfigDict(from_attributes=True) # Pydantic read data directly from a database object


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


# ML 
class MLRequest(BaseModel):
    features: dict[str, float]
    

class PredictRequest(BaseModel):
    features: dict[str, float]
    model_config = ConfigDict(json_schema_extra={
        'examples' : [{
            "features" : {
                "RevolvingUtilizationOfUnsecuredLines": 0.766,
                "age": 45,
                "NumberOfTime30-59DaysPastDueNotWorse": 2,
                "DebtRatio": 0.803,
                "MonthlyIncome": 9120,
                "NumberOfOpenCreditLinesAndLoans": 13,
                "NumberOfTimes90DaysLate": 0,
                "NumberRealEstateLoansOrLines": 6,
                "NumberOfTime60-89DaysPastDueNotWorse": 0,
                "NumberOfDependents": 2,
            }
        }] 
    }) 

class PredictResponse(BaseModel):
    prediction: int
    probability: float

class SegmentRequest(BaseModel):
    features: dict[str, float]
    model_config = ConfigDict(json_schema_extra={
        'examples' : [{
            'features':{
                "BALANCE": 2100.0,
                "BALANCE_FREQUENCY": 1.0,
                "PURCHASES": 3400.0,
                "ONEOFF_PURCHASES": 2000.0,
                "INSTALLMENTS_PURCHASES": 1400.0,
                "CASH_ADVANCE": 0.0,
                "PURCHASES_FREQUENCY": 1.0,
                "ONEOFF_PURCHASES_FREQUENCY": 0.8,
                "PURCHASES_INSTALLMENTS_FREQUENCY": 0.7,
                "CASH_ADVANCE_FREQUENCY": 0.0,
                "CASH_ADVANCE_TRX": 0,
                "PURCHASES_TRX": 45,
                "CREDIT_LIMIT": 7500.0,
                "PAYMENTS": 3300.0,
                "MINIMUM_PAYMENTS": 600.0,
                "PRC_FULL_PAYMENT": 0.0,
                "TENURE": 12,
            }
        }]
    })

class SegmentResponse(BaseModel):
    cluster_id: int 
    name: str
    description: str
    icon : str


# RAG 
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str 
    sources: list[str]
    log_id: int 


# Logs & feedback 
class LogOut(BaseModel):
    id: int 
    endpoint: str
    input_text: Optional[str]
    output_text: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class FeedbackCreate(BaseModel):
    rating: int = Field(ge = 1, le = 5)
    comment: Optional[str] = None
    log_id: Optional[int] = None 


class FeedbackOut(BaseModel):
    id: int 
    rating: int 
    comment: Optional[str]
    log_id: Optional[int]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

    