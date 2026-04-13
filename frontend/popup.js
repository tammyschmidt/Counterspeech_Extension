// Counterspeech Extension - Popup Script

console.log('Counter Speech Extension loaded');

// API configuration
// const API_BASE_URL = 'http://127.0.0.1:8000/api'; // local backend
const API_BASE_URL = 'https://counterspeechextension-production.up.railway.app/api'; // deployed backend on Railway

// DOM Elements
const hatefulCommentInput = document.getElementById('hateful-comment');
const additionalInputInput = document.getElementById('additional-input');
const roleOptions = document.querySelectorAll('.role-option');
const writingStyleOptions = document.querySelectorAll('.style-option');
const lengthSlider = document.getElementById('length-slider');
const lengthValueDisplay = document.getElementById('length-value');
const usePlaceholdersCheckbox = document.getElementById('use-placeholders');
const generateBtn = document.getElementById('generate-btn');
const loadingDiv = document.getElementById('loading');
const suggestionsDiv = document.getElementById('suggestions');
const suggestionsList = document.getElementById('suggestions-list');

// Window Elements
const headerBtn = document.getElementById('info-btn');
const generationWindow = document.getElementById('generation-window');
const infoWindow = document.getElementById('info-window');

// Selected role
let selectedRole = null;

// Selected writing style
let selectedWritingStyle = null;

// Consent Elements
const consentPrivacy = document.getElementById('consent-privacy');
const consentAccountability = document.getElementById('consent-accountability');
const consentEthical = document.getElementById('consent-ethical');

// Consent state
let consentState = {
    privacy: false,
    accountability: false,
    ethical: false
};

// Helper function to safely access chrome.storage
function getStorage() {
    try {
        if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
            return chrome.storage.local;
        }

        if (typeof window !== 'undefined' && window.chrome && window.chrome.storage && window.chrome.storage.local) {
            return window.chrome.storage.local;
        }
        
        console.error('Chrome storage API not available. Make sure the extension is reloaded and has storage permission.');
        return null;
    } catch (error) {
        console.error('Error accessing chrome storage:', error);
        return null;
    }
}

// Load consent state from storage
async function loadConsentState() {
    try {
        const storage = getStorage();
        if (!storage) {
            console.error('Chrome storage API not available');
            return;
        }
        
        const result = await storage.get(['consentPrivacy', 'consentAccountability', 'consentEthical']);
        
        if (result.consentPrivacy !== undefined) {
            consentState.privacy = result.consentPrivacy;
        }
        if (result.consentAccountability !== undefined) {
            consentState.accountability = result.consentAccountability;
        }
        if (result.consentEthical !== undefined) {
            consentState.ethical = result.consentEthical;
        }
        

        if (consentPrivacy) {
            consentPrivacy.checked = consentState.privacy;
        }
        if (consentAccountability) {
            consentAccountability.checked = consentState.accountability;
        }
        if (consentEthical) {
            consentEthical.checked = consentState.ethical;
        }
        
        console.log('Consent state loaded:', consentState);
    } catch (error) {
        console.error('Error loading consent state:', error);
    }
}

// Save consent state to storage
async function saveConsentState() {
    try {
        const storage = getStorage();
        if (!storage) {
            console.error('Chrome storage API not available');
            return;
        }
        
        const data = {
            consentPrivacy: consentState.privacy,
            consentAccountability: consentState.accountability,
            consentEthical: consentState.ethical
        };
        await storage.set(data);
        console.log('Consent state saved:', data);
        
        const verify = await storage.get(['consentPrivacy', 'consentAccountability', 'consentEthical']);
        console.log('Consent state verified:', verify);
    } catch (error) {
        console.error('Error saving consent state:', error);
    }
}

// Check if all consents are given
function hasAllConsents() {
    return consentState.privacy && consentState.accountability && consentState.ethical;
}

// Initialize everything when DOM is ready
function initialize() {
    loadConsentState();
}

// Ensure DOM is ready before initializing
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    initialize();
}


// Consent toggle handlers
if (consentPrivacy) {
    consentPrivacy.addEventListener('change', (e) => {
        consentState.privacy = e.target.checked;
        saveConsentState();
    });
}

if (consentAccountability) {
    consentAccountability.addEventListener('change', (e) => {
        consentState.accountability = e.target.checked;
        saveConsentState();
    });
}

if (consentEthical) {
    consentEthical.addEventListener('change', (e) => {
        consentState.ethical = e.target.checked;
        saveConsentState();
    });
}

// Show different windows
function showInfoWindow() {
    generationWindow.classList.remove('active');
    infoWindow.classList.add('active');
    if (headerBtn) headerBtn.textContent = 'Back to Generator';
}
function showGenerationWindow() {
    infoWindow.classList.remove('active');
    generationWindow.classList.add('active');
    if (headerBtn) headerBtn.textContent = 'Info';
}
if (headerBtn) {
    headerBtn.addEventListener('click', () => {
        if (infoWindow.classList.contains('active')) {
            showGenerationWindow();
        } else {
            showInfoWindow();
        }
    });
}

// Length labels mapping with descriptions
const lengthLabels = {
    1: { name: 'Short', description: '(20-40 words)' },
    2: { name: 'Medium', description: '(40-80 words)' },
    3: { name: 'Long', description: '(80-120 words)' }
};

// Update length display when slider changes
lengthSlider.addEventListener('input', (e) => {
    const value = parseInt(e.target.value);
    const label = lengthLabels[value] || lengthLabels[2];
    lengthValueDisplay.innerHTML = `${label.name}<br>${label.description}`;
});

// Initialize length display
const initialValue = parseInt(lengthSlider.value);
const initialLabel = lengthLabels[initialValue] || lengthLabels[2];
lengthValueDisplay.innerHTML = `${initialLabel.name}<br>${initialLabel.description}`;

// Role and Writing style selection handlers
if (generationWindow) {
    generationWindow.addEventListener('click', (e) => {
        const roleOpt = e.target.closest('.role-option');
        if (roleOpt) {
            document.querySelectorAll('.role-option').forEach(opt => opt.classList.remove('selected'));
            roleOpt.classList.add('selected');
            selectedRole = roleOpt.getAttribute('data-role');
            return;
        }
        const styleOpt = e.target.closest('.style-option');
        if (styleOpt) {
            document.querySelectorAll('.style-option').forEach(opt => opt.classList.remove('selected'));
            styleOpt.classList.add('selected');
            selectedWritingStyle = styleOpt.getAttribute('data-style');
        }
    });
}

// Generate button click handler
generateBtn.addEventListener('click', async () => {
    // Check consent first
    if (!hasAllConsents()) {
        alert('Please first give your consent on the info page.');
        showInfoWindow();
        return;
    }

    // Validate inputs
    if (!hatefulCommentInput.value.trim()) {
        alert('Please paste a hateful comment first.');
        return;
    }

    if (!additionalInputInput.value.trim()) {
        alert('Please give your input first.');
        return;
    }

    if (!selectedRole) {
        alert('Please select your role.');
        return;
    }

    if (!selectedWritingStyle) {
        alert('Please select a writing style.');
        return;
    }

    // Show loading state
    generateBtn.disabled = true;
    loadingDiv.classList.remove('hidden');
    suggestionsDiv.classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                hateful_comment: hatefulCommentInput.value,
                additional_input: additionalInputInput.value || null,
                role: selectedRole,
                writing_style: selectedWritingStyle,
                length: parseInt(lengthSlider.value),
                use_placeholders: document.getElementById('use-placeholders')?.checked ?? false
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        const suggestions = (data?.suggestions || [])
            .map(item => (item.text || '').trim())
            .filter(text => text.length > 0);

        if (!suggestions.length) {
            suggestions.push('No response generated. Please try again.');
        }

        displaySuggestions(suggestions);
    } catch (error) {
        console.error('Error generating counterspeech', error);
        alert('Something went wrong while generating the counterspeech. Please try again.');
    } finally {
        loadingDiv.classList.add('hidden');
        generateBtn.disabled = false;
    }
});

// Display suggestions
function displaySuggestions(suggestions) {
    suggestionsList.innerHTML = '';
    
    suggestions.forEach((suggestion, index) => {
        const suggestionItem = document.createElement('div');
        suggestionItem.className = 'suggestion-item';
        
        const suggestionText = document.createElement('div');
        suggestionText.className = 'suggestion-text';
        suggestionText.textContent = suggestion;
        
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'suggestion-actions';
        
        const editBtn = document.createElement('button');
        editBtn.className = 'btn btn-edit';
        editBtn.textContent = 'Edit';
        editBtn.addEventListener('click', () => {
            if (suggestionText.contentEditable === 'true') {
                // Save mode
                suggestionText.contentEditable = 'false';
                editBtn.textContent = 'Edit';
            } else {
                // Edit mode
                suggestionText.contentEditable = 'true';
                suggestionText.focus();
                editBtn.textContent = 'Save';
            }
        });
        
        const copyBtn = document.createElement('button');
        copyBtn.className = 'btn btn-copy';
        copyBtn.textContent = 'Copy';
        copyBtn.addEventListener('click', () => {
            const textToCopy = suggestionText.textContent;
            navigator.clipboard.writeText(textToCopy).then(() => {
                copyBtn.textContent = 'Copied!';
                copyBtn.classList.add('copied');
                setTimeout(() => {
                    copyBtn.textContent = 'Copy';
                    copyBtn.classList.remove('copied');
                }, 2000);
            });
        });
        
        actionsDiv.appendChild(editBtn);
        actionsDiv.appendChild(copyBtn);
        
        suggestionItem.appendChild(suggestionText);
        suggestionItem.appendChild(actionsDiv);
        
        suggestionsList.appendChild(suggestionItem);
    });
    
    suggestionsDiv.classList.remove('hidden');
    suggestionsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
