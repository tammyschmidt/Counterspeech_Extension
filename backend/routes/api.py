# API route handlers

from fastapi import APIRouter, HTTPException
from models.schemas import GenerateRequest, GenerateResponse, CounterspeechSuggestion
from services.groq_service import GroqService
from services.retrieval_service import RetrievalService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["counterspeech"])

# Initialize services
groq_service = GroqService()
retrieval_service = RetrievalService()

# POST generation request
@router.post("/generate", response_model=GenerateResponse)
async def generate_counterspeech(request: GenerateRequest):
    """
    Generate counterspeech suggestions based on hateful comment and given user input
    
    Args:
        request: GenerateRequest containing hateful comment, additional input, role, style, length, placeholder preference
        
    Returns:
        GenerateResponse with three counterspeech suggestions
    """
    try:
        # Validate role
        valid_roles = ["target", "target-group", "ally"]
        if request.role not in valid_roles:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
        
        # Validate writing style
        valid_styles = ["formal", "familiar"]
        if request.writing_style not in valid_styles:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid writing style. Must be one of: {', '.join(valid_styles)}"
            )
        
        # Retrieve similar CONAN examples
        examples = retrieval_service.get_similar_examples(
            hateful_comment=request.hateful_comment
        )

        # Generate counterspeech with contextual examples
        suggestions_text = groq_service.generate_counterspeech(
            hateful_comment=request.hateful_comment,
            additional_input=request.additional_input,
            role=request.role,
            writing_style=request.writing_style,
            length=request.length,
            examples=examples,
            use_placeholders=request.use_placeholders,
        )
        
        # Format response
        suggestions = [
            CounterspeechSuggestion(text=text) 
            for text in suggestions_text
        ]
        
        return GenerateResponse(suggestions=suggestions)
        
    except Exception as e:
        logger.error(f"Error generating counterspeech: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating counterspeech: {str(e)}"
        )

# GET health check
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "counterspeech-api"}

