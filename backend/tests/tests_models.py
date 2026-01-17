import pytest
from pydantic import ValidationError
from app.models.schemas import (
    PromptRequest,
    ClarifyRequest,
    ClarifyResponse,
    AnalysisResponse
)


class TestPromptRequest:
    """Tests for PromptRequest schema."""
    
    def test_valid_prompt_request(self):
        """Test creating a valid PromptRequest."""
        request = PromptRequest(prompt="What is AI?")
        
        assert request.prompt == "What is AI?"
        assert request.clarification is None
    
    def test_prompt_request_with_clarification(self):
        """Test PromptRequest with clarification field."""
        request = PromptRequest(
            prompt="How does hacking work?",
            clarification="For educational purposes"
        )
        
        assert request.prompt == "How does hacking work?"
        assert request.clarification == "For educational purposes"
    
    def test_empty_prompt_raises_validation_error(self):
        """Test that empty prompt is rejected by validator."""
        with pytest.raises(ValidationError) as exc_info:
            PromptRequest(prompt="")
        
        assert "cannot be empty" in str(exc_info.value).lower()
    
    def test_whitespace_prompt_raises_validation_error(self):
        """Test that whitespace-only prompt is rejected."""
        with pytest.raises(ValidationError):
            PromptRequest(prompt="    ")
    
    def test_prompt_is_stripped(self):
        """Test that prompt whitespace is trimmed."""
        request = PromptRequest(prompt="  test prompt  ")
        
        assert request.prompt == "test prompt"
        assert not request.prompt.startswith(" ")
        assert not request.prompt.endswith(" ")
    
    def test_missing_prompt_field_raises_error(self):
        """Test that missing prompt field is rejected."""
        with pytest.raises(ValidationError):
            PromptRequest()


class TestClarifyRequest:
    """Tests for ClarifyRequest schema."""
    
    def test_valid_clarify_request(self):
        """Test creating a valid ClarifyRequest."""
        request = ClarifyRequest(prompt="test prompt")
        
        assert request.prompt == "test prompt"


class TestClarifyResponse:
    """Tests for ClarifyResponse schema."""
    
    def test_no_clarification_needed(self):
        """Test response when no clarification needed."""
        response = ClarifyResponse(
            needs_clarification=False,
            question=None
        )
        
        assert response.needs_clarification == False
        assert response.question is None
    
    def test_clarification_needed_with_question(self):
        """Test response when clarification is needed."""
        response = ClarifyResponse(
            needs_clarification=True,
            question="What is your intent?"
        )
        
        assert response.needs_clarification == True
        assert response.question == "What is your intent?"
    
    def test_clarification_needed_requires_bool(self):
        """Test that needs_clarification must be boolean."""
        with pytest.raises(ValidationError):
            ClarifyResponse(
                needs_clarification="yes",  # String instead of bool
                question="test"
            )


class TestAnalysisResponse:
    """Tests for AnalysisResponse schema."""
    
    def test_valid_low_risk_response(self):
        """Test creating a low risk analysis response."""
        response = AnalysisResponse(
            risk_level="Low",
            category="Benign",
            reasons=["Safe question"],
            suspicious_phrases=[]
        )
        
        assert response.risk_level == "Low"
        assert response.category == "Benign"
        assert len(response.reasons) == 1
        assert len(response.suspicious_phrases) == 0
    
    def test_valid_high_risk_response(self):
        """Test creating a high risk analysis response."""
        response = AnalysisResponse(
            risk_level="High",
            category="Prompt Injection",
            reasons=["Instruction override", "Suspicious pattern"],
            suspicious_phrases=["ignore previous instructions"]
        )
        
        assert response.risk_level == "High"
        assert response.category == "Prompt Injection"
        assert len(response.reasons) == 2
        assert len(response.suspicious_phrases) == 1
    
    def test_missing_required_fields_raises_error(self):
        """Test that missing required fields cause validation error."""
        with pytest.raises(ValidationError):
            AnalysisResponse(
                risk_level="Low"
                # Missing category, reasons, suspicious_phrases
            )
    
    def test_reasons_must_be_list(self):
        """Test that reasons field must be a list."""
        with pytest.raises(ValidationError):
            AnalysisResponse(
                risk_level="Low",
                category="Benign",
                reasons="This is not a list",  # Should be List[str]
                suspicious_phrases=[]
            )
    
    def test_suspicious_phrases_must_be_list(self):
        """Test that suspicious_phrases field must be a list."""
        with pytest.raises(ValidationError):
            AnalysisResponse(
                risk_level="Low",
                category="Benign",
                reasons=[],
                suspicious_phrases="not a list"  # Should be List[str]
            )