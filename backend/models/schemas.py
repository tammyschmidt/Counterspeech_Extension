# Data models for request/response

from pydantic import BaseModel, Field
from typing import Optional, List


class GenerateRequest(BaseModel):
    """Request model for generating counter speech suggestions"""
    hateful_comment: str = Field(..., description="The hateful comment to respond to")
    additional_input: Optional[str] = Field(None, description="Optional additional input from the user")
    role: str = Field(..., description="User's role: 'target', 'target-group', or 'ally'")
    writing_style: str = Field(..., description="Writing style: 'formal' or 'familiar'")

    class Config:
        json_schema_extra = {
            "example": {
                "hateful_comment": "Example hateful comment here",
                "additional_input": "Optional personal context",
                "role": "ally",
                "writing_style": "formal"
            }
        }


class CounterSpeechSuggestion(BaseModel):
    """Model for a single counter speech suggestion"""
    text: str = Field(..., description="The counter speech suggestion text")


class GenerateResponse(BaseModel):
    """Response model containing counter speech suggestions"""
    suggestions: List[CounterSpeechSuggestion] = Field(..., description="List of counter speech suggestions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "suggestions": [
                    {"text": "First counter speech suggestion"},
                    {"text": "Second counter speech suggestion"},
                    {"text": "Third counter speech suggestion"}
                ]
            }
        }

