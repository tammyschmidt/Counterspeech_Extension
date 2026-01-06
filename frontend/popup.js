// Counter Speech Extension - Popup Script

console.log('Counter Speech Extension loaded');

// API configuration
const API_BASE_URL = 'http://127.0.0.1:8000/api';

// DOM Elements
const hatefulCommentInput = document.getElementById('hateful-comment');
const additionalInputInput = document.getElementById('additional-input');
const roleOptions = document.querySelectorAll('.role-option');
const writingStyleSelect = document.getElementById('writing-style');
const generateBtn = document.getElementById('generate-btn');
const loadingDiv = document.getElementById('loading');
const suggestionsDiv = document.getElementById('suggestions');
const suggestionsList = document.getElementById('suggestions-list');

// Selected role
let selectedRole = null;

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

// Generate button click handler
generateBtn.addEventListener('click', async () => {
    // Validate inputs
    if (!hatefulCommentInput.value.trim()) {
        alert('Please paste a hateful comment first.');
        return;
    }

    if (!selectedRole) {
        alert('Please select your role.');
        return;
    }

    const writingStyle = writingStyleSelect.value;
    if (!writingStyle) {
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
                writing_style: writingStyle
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
}
