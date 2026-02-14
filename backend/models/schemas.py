# Data models for request/response

from pydantic import BaseModel, Field
from typing import Optional, List


class GenerateRequest(BaseModel):
    """Request model for generating counter speech suggestions"""
    hateful_comment: str = Field(..., description="The hateful comment to respond to")
    additional_input: Optional[str] = Field(None, description="Optional additional input from the user")
    role: str = Field(..., description="User's role: 'target', 'target-group', or 'ally'")
    writing_style: str = Field(..., description="Writing style: 'formal' or 'familiar'")
    length: int = Field(default=2, ge=1, le=3, description="Response length on a scale of 1-3 (1=Short 20-40 words, 2=Medium 40-80 words, 3=Long 80-120 words)")
    use_placeholders: bool = Field(
        default=False,
        description="Whether to include explicit placeholders the user can later fill with personal details",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "hateful_comment": "Example hateful comment here",
                "additional_input": "Optional personal context",
                "role": "ally",
                "writing_style": "formal",
                "length": 2,
                "use_placeholders": True,
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

