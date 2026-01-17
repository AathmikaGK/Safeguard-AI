# SafePrompt - Prompt Injection Risk Analyzer

A simple web application to analyze AI prompts for security risks 

## Features

- Analyze prompts for injection risks
- Context-aware analysis
- Multi-layer detection (heuristics + LLM)
- Comprehensive test suite (85%+ coverage)

## Tech Stack

- **Backend**: Python + FastAPI
- **Frontend**: HTML + Bootstrap 5
- **AI**: Anthropic Claude API

## Setup
### Prerequisites

- Python 3.11+
- Anthropic API key- Get your API key from: https://console.anthropic.com/
# Clone repository
git clone 
cd safeguard-ai/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```
# Run the Application

```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload
```

# Open in Browser

Navigate to: http://localhost:8000

## Testing
```bash
# Run all tests
pytest
```

## Usage

1. Select the context where your prompt will be used
2. Paste your prompt in the text area
3. Click "Analyze Prompt"
4. Review the risk assessment and safe version
5. Copy the safe version to use in your application

## API Endpoints

### `POST /analyze`

Analyze a prompt for security risks.

**Request Body:**
```json
{
  "prompt": "Your prompt here",
  "context": "general"
}
```

**Response:**
```json
{
  "risk_level": "Medium",
  "risk_score": 65,
  "issues_found": ["Issue 1", "Issue 2"],
  "explanation": "Detailed explanation...",
  "safe_version": "Safer version of the prompt..."
}
```

### `GET /health`

Health check endpoint.

## Future Enhancements

- [ ] Add more context types
- [ ] Export analysis reports
- [ ] API rate limiting
- [ ] User authentication
- [ ] Batch analysis
- [ ] Historical analysis tracking
- [ ] Custom rule definitions

## License

MIT
