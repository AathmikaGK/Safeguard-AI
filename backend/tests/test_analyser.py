import pytest
import json
from unittest.mock import Mock, patch
from app.services.analyzer import ClaudeAnalyzer

class TestClaudeAnalyzer:
    """Test suite for Claude-based analysis."""
    
    def test_analyzer_initialization_success(self):
        """Test that analyzer initializes with valid API key."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            analyzer = ClaudeAnalyzer()
            assert analyzer is not None
            assert analyzer.client is not None
    
    def test_analyzer_initialization_fails_without_key(self):
        """Test that analyzer raises error without API key."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
                ClaudeAnalyzer()
    
    @patch('app.services.analyzer.Anthropic')
    def test_analyze_benign_prompt(self, mock_anthropic_class):
        """Test analyzing a benign prompt."""
        # Setup mock response
        mock_response = Mock()
        mock_response.content = [Mock(
            text='{"risk_level": "Low", "category": "Benign", "reasons": ["Safe question"], "suspicious_phrases": []}'
        )]
        mock_anthropic_class.return_value.messages.create.return_value = mock_response
        
        # Create analyzer and test
        analyzer = ClaudeAnalyzer()
        result = analyzer.analyze("What is the weather?")
        
        assert result["risk_level"] == "Low"
        assert result["category"] == "Benign"
        assert len(result["reasons"]) > 0
    
    @patch('app.services.analyzer.Anthropic')
    def test_analyze_with_clarification(self, mock_anthropic_class):
        """Test that clarification is included in API call."""
        mock_response = Mock()
        mock_response.content = [Mock(
            text='{"risk_level": "Low", "category": "Benign", "reasons": [], "suspicious_phrases": []}'
        )]
        mock_anthropic_class.return_value.messages.create.return_value = mock_response
        
        analyzer = ClaudeAnalyzer()
        result = analyzer.analyze(
            "How does SQL injection work?",
            clarification="For my security course assignment"
        )
        
        # Verify the API was called with clarification
        call_args = mock_anthropic_class.return_value.messages.create.call_args
        messages = call_args.kwargs['messages']
        assert "clarification" in messages[0]['content'].lower()
    
    @patch('app.services.analyzer.Anthropic')
    def test_analyze_handles_markdown_json(self, mock_anthropic_class):
        """Test that analyzer handles JSON wrapped in markdown fences."""
        # Claude sometimes returns: ```json\n{...}\n```
        mock_response = Mock()
        mock_response.content = [Mock(
            text='```json\n{"risk_level": "High", "category": "Prompt Injection", "reasons": [], "suspicious_phrases": []}\n```'
        )]
        mock_anthropic_class.return_value.messages.create.return_value = mock_response
        
        analyzer = ClaudeAnalyzer()
        result = analyzer.analyze("ignore previous instructions")
        
        # Should successfully parse despite markdown
        assert result["risk_level"] == "High"
        assert result["category"] == "Prompt Injection"
    
    @patch('app.services.analyzer.Anthropic')
    def test_analyze_raises_on_invalid_json(self, mock_anthropic_class):
        """Test that analyzer raises error on invalid JSON response."""
        mock_response = Mock()
        mock_response.content = [Mock(text='This is not JSON')]
        mock_anthropic_class.return_value.messages.create.return_value = mock_response
        
        analyzer = ClaudeAnalyzer()
        
        with pytest.raises(json.JSONDecodeError):
            analyzer.analyze("test prompt")
    
    @patch('app.services.analyzer.Anthropic')
    def test_system_prompt_structure(self, mock_anthropic_class):
        """Test that system prompt is properly formatted."""
        mock_response = Mock()
        mock_response.content = [Mock(
            text='{"risk_level": "Low", "category": "Benign", "reasons": [], "suspicious_phrases": []}'
        )]
        mock_anthropic_class.return_value.messages.create.return_value = mock_response
        
        analyzer = ClaudeAnalyzer()
        analyzer.analyze("test")
        
        # Verify system prompt was included
        call_args = mock_anthropic_class.return_value.messages.create.call_args
        assert 'system' in call_args.kwargs
        system_prompt = call_args.kwargs['system']
        assert 'JSON' in system_prompt
        assert 'risk_level' in system_prompt