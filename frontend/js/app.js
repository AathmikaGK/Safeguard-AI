const API_BASE_URL = 'http://localhost:8000'; // Change for production

async function analyzePrompt() {
    const prompt = document.getElementById('promptInput').value.trim();
    if (!prompt) {
        alert('Please enter a prompt to analyze');
        return;
    }

    const clarificationSection = document.getElementById('clarificationSection');
    const clarificationInput = document.getElementById('clarificationInput');
    const clarification = clarificationInput ? clarificationInput.value.trim() : "";

    // If clarification section is visible and user has entered clarification,
    // go straight to /analyze with both prompt + clarification
    if (clarificationSection.style.display !== 'none' && clarification) {
        await callAnalyzeApi(prompt, clarification);
        return;
    }

    // Otherwise, first ask if clarification is needed
    await callClarifyApi(prompt);
}

/**
 * Call /clarify endpoint to check if user intent needs clarification
 */
async function callClarifyApi(prompt) {
    showLoading(true);
    hideResults();
    hideClarification();

    try {
        const response = await fetch(`${API_BASE_URL}/clarify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt })
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || 'Clarification check failed');
        }

        const data = await response.json();

        if (data.needs_clarification) {
            // Show clarification question to user
            showClarificationQuestion(data.question);
        } else {
            // No clarification needed → go straight to analysis
            await callAnalyzeApi(prompt, "");
        }

    } catch (error) {
        alert('Error during clarification: ' + error.message);
        console.error(error);
    } finally {
        showLoading(false);
    }
}

/**
 * Call /analyze endpoint to get risk assessment
 */
async function callAnalyzeApi(prompt, clarification) {
    showLoading(true);
    hideResults();

    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: prompt,
                clarification: clarification || null
            })
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || 'Analysis failed');
        }

        const data = await response.json();
        displayResults(data, prompt);

    } catch (error) {
        alert('Error analyzing prompt: ' + error.message);
        console.error(error);
    } finally {
        showLoading(false);
    }
}

/**
 * Display analysis results to user
 */
function displayResults(data, originalPrompt) {
    // Update risk badge
    const riskBadge = document.getElementById('riskBadge');
    riskBadge.textContent = data.risk_level;
    riskBadge.className = 'badge risk-badge risk-' + data.risk_level.toLowerCase();

    // Update category badge
    const categoryBadge = document.getElementById('categoryBadge');
    categoryBadge.textContent = data.category;

    // Color code category
    if (data.category === 'Benign') {
        categoryBadge.className = 'badge bg-success fs-6 p-2';
    } else if (data.category === 'Prompt Injection') {
        categoryBadge.className = 'badge bg-danger fs-6 p-2';
    } else if (data.category === 'Data Exfiltration') {
        categoryBadge.className = 'badge bg-warning text-dark fs-6 p-2';
    } else {
        categoryBadge.className = 'badge bg-secondary fs-6 p-2';
    }

    // Update reasons list
    const reasonsList = document.getElementById('reasonsList');
    reasonsList.innerHTML = '';
    data.reasons.forEach(reason => {
        const li = document.createElement('li');
        li.className = 'list-group-item';
        li.textContent = reason;
        reasonsList.appendChild(li);
    });

    // Update suspicious phrases
    const suspiciousPhrasesDiv = document.getElementById('suspiciousPhrases');
    if (data.suspicious_phrases.length === 0) {
        suspiciousPhrasesDiv.innerHTML = '<p class="mb-0 text-success">✓ No suspicious phrases detected</p>';
        suspiciousPhrasesDiv.className = 'alert alert-success';
    } else {
        suspiciousPhrasesDiv.className = 'alert alert-warning';
        suspiciousPhrasesDiv.innerHTML = '<p class="mb-2"><strong>Detected suspicious phrases:</strong></p>';
        data.suspicious_phrases.forEach(phrase => {
            const span = document.createElement('span');
            span.className = 'suspicious-highlight';
            span.textContent = phrase;
            suspiciousPhrasesDiv.appendChild(span);
            suspiciousPhrasesDiv.appendChild(document.createTextNode(' '));
        });
    }

    // Show results section
    document.getElementById('resultsSection').style.display = 'block';

    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}

/**
 * Show clarification question to user
 */
function showClarificationQuestion(question) {
    const clarificationSection = document.getElementById('clarificationSection');
    const questionEl = document.getElementById('clarificationQuestion');
    const clarificationInput = document.getElementById('clarificationInput');
    
    questionEl.textContent = question || "Please provide more context for your prompt.";
    clarificationInput.value = "";
    clarificationSection.style.display = 'block';
}

/**
 * Submit clarification and re-analyze
 */
function submitClarificationAndAnalyze() {
    analyzePrompt();
}

// UI Helper Functions
function showLoading(show) {
    document.querySelector('.loading').style.display = show ? 'block' : 'none';
}

function hideResults() {
    document.getElementById('resultsSection').style.display = 'none';
}

function hideClarification() {
    document.getElementById('clarificationSection').style.display = 'none';
}

// Keyboard shortcut: Ctrl/Cmd + Enter to analyze
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('promptInput').addEventListener('keydown', function (e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            analyzePrompt();
        }
    });
});