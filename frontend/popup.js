// Counter Speech Extension - Popup Script

console.log('Counter Speech Extension loaded');

// API configuration
const API_BASE_URL = 'http://127.0.0.1:8000/api';

// DOM Elements
const hatefulCommentInput = document.getElementById('hateful-comment');
const additionalInputInput = document.getElementById('additional-input');
const roleOptions = document.querySelectorAll('.role-option');
const writingStyleOptions = document.querySelectorAll('.style-option');
const lengthSlider = document.getElementById('length-slider');
const lengthValueDisplay = document.getElementById('length-value');
const generateBtn = document.getElementById('generate-btn');
const loadingDiv = document.getElementById('loading');
const suggestionsDiv = document.getElementById('suggestions');
const suggestionsList = document.getElementById('suggestions-list');

// Window/Tab Elements
const windowTabs = document.querySelectorAll('.window-tab');
const generationWindow = document.getElementById('generation-window');
const infoWindow = document.getElementById('info-window');

// Consent Elements
const consentPrivacy = document.getElementById('consent-privacy');
const consentAccountability = document.getElementById('consent-accountability');
const consentEthical = document.getElementById('consent-ethical');

// Selected role
let selectedRole = null;

// Selected writing style
let selectedWritingStyle = null;

// Consent state
let consentState = {
    privacy: false,
    accountability: false,
    ethical: false
};

// Helper function to safely access chrome.storage
function getStorage() {
    try {
        // In Chrome extensions, chrome should be globally available
        // Check if chrome and chrome.storage.local exist
        if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
            return chrome.storage.local;
        }
        
        // Fallback to window.chrome if needed
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
        
        // Update checkboxes if they exist
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
        
        // Verify it was saved
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
    // Load consent state
    loadConsentState();
}

// Ensure DOM is ready before initializing
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    // DOM is already ready
    initialize();
}

// Tab switching functionality
windowTabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const targetWindow = tab.getAttribute('data-window');
        
        // Update active tab
        windowTabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        // Update active window
        generationWindow.classList.remove('active');
        infoWindow.classList.remove('active');
        
        if (targetWindow === 'generation') {
            generationWindow.classList.add('active');
        } else if (targetWindow === 'info') {
            infoWindow.classList.add('active');
        }
    });
});

// Consent toggle handlers - attach after ensuring elements exist
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

// Role selection handlers
roleOptions.forEach(option => {
    option.addEventListener('click', () => {
        // Remove selected class from all options
        roleOptions.forEach(opt => opt.classList.remove('selected'));
        // Add selected class to clicked option
        option.classList.add('selected');
        // Store selected role value
        selectedRole = option.getAttribute('data-role');
    });
});

// Writing style selection handlers
writingStyleOptions.forEach(option => {
    option.addEventListener('click', () => {
        // Remove selected class from all options
        writingStyleOptions.forEach(opt => opt.classList.remove('selected'));
        // Add selected class to clicked option
        option.classList.add('selected');
        // Store selected writing style value
        selectedWritingStyle = option.getAttribute('data-style');
    });
});

// Generate button click handler
generateBtn.addEventListener('click', async () => {
    // Check consent first
    if (!hasAllConsents()) {
        alert('Please first give your consent on the info page.');
        // Switch to info tab
        windowTabs.forEach(t => t.classList.remove('active'));
        const infoTab = document.querySelector('.window-tab[data-window="info"]');
        if (infoTab) {
            infoTab.classList.add('active');
            generationWindow.classList.remove('active');
            infoWindow.classList.add('active');
        }
        return;
    }

    // Validate inputs
    if (!hatefulCommentInput.value.trim()) {
        alert('Please paste a hateful comment first.');
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
                length: parseInt(lengthSlider.value)
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
        console.error('Error generating counter speech', error);
        alert('Something went wrong while generating the counter speech. Please try again.');
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
    // Bring suggestions into view so the user does not miss them
    suggestionsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
