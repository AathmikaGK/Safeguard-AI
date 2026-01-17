from fastapi import APIRouter, HTTPException, status

from app.models.schemas import (
    PromptRequest,
    AnalysisResponse,
    ClarifyRequest,
    ClarifyResponse
)
from app.services.detector import HeuristicDetector
from app.services.analyzer import ClaudeAnalyzer
from app.services.clarifier import ClarificationService
from app.config import settings

router = APIRouter()

detector = HeuristicDetector()
analyzer = ClaudeAnalyzer()
clarifier = ClarificationService()

@router.post(
    "/clarify",
    response_model=ClarifyResponse,
    summary="Check if prompt needs clarification",
    description="Determines if a prompt is ambiguous and needs user clarification"
)
async def clarify_prompt(request: ClarifyRequest):
    """
    Check if a prompt needs clarification before analysis.
    
    This is called first to determine if the prompt is:
    - Obviously malicious (no clarification needed)
    - Dual-use/ambiguous (clarification needed)
    - Clearly benign (no clarification needed)
    """
    if not request.prompt.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt cannot be empty"
        )
    
    response = clarifier.check_needs_clarification(request.prompt)
    return response


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analyze prompt for security risks",
    description="Multi-layer analysis using heuristics and Claude AI"
)
async def analyze_prompt(request: PromptRequest):
    """
    Analyze a prompt for injection risks.
    
    Process:
    1. Run heuristic detection (fast, rule-based)
    2. Call Claude for semantic analysis (slower, AI-based)
    3. Merge results
    4. Normalize risk level
    5. Return combined analysis
    """
    if not request.prompt.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Prompt cannot be empty"
        )
    
    try:
        heuristic_issues, heuristic_spans = detector.analyze(request.prompt)
        
        claude_result = analyzer.analyze(request.prompt, request.clarification)

        combined_reasons = (
            claude_result.get("reasons", []) +
            heuristic_issues
        )
        
        claude_phrases = claude_result.get("suspicious_phrases", [])
        all_phrases = claude_phrases + heuristic_spans
        seen = set()
        dedup_phrases = []
        for phrase in all_phrases:
            if phrase not in seen:
                seen.add(phrase)
                dedup_phrases.append(phrase)

        risk_level = claude_result.get("risk_level", "Low")
        if isinstance(risk_level, str):
            rl_normalized = risk_level.strip().lower()
            if rl_normalized.startswith("high"):
                risk_level = "High"
            elif rl_normalized.startswith("medium"):
                risk_level = "Medium"
            else:
                risk_level = "Low"
        
        category = claude_result.get("category", "Benign")
        
        return AnalysisResponse(
            risk_level=risk_level,
            category=category,
            reasons=combined_reasons,
            suspicious_phrases=dedup_phrases,
        )
    
    except Exception as e:
        # Log the error 
        print(f"Error analyzing prompt: {repr(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/health", summary="Health check endpoint")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.API_TITLE,
        "version": settings.API_VERSION
    }