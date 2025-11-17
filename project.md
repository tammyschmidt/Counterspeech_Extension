# Technical Development Scope: Development of a Browser Extension for Human-AI Collaboration for Counter Speech (CS) against Hate Speech (HS)

## Summary

This project will develop a browser extension to facilitate human-AI collaboration in countering online hate speech (HS) through effective and authentic counter speech (CS). The extension aims to lower barriers to engagement—such as limited time, emotional strain, and uncertainty about how to respond—by providing users with AI-generated CS suggestions that they can personalize. The system leverages a state-of-the-art language model, a retrieval engine, and embedding technologies to generate contextually relevant and impactful responses. The ultimate goal is to empower individuals, whether targets or allies, to participate constructively in online discourse.

---

## Scope of Technical Development

**Core Components:**

- **Browser Extension (Frontend):**

  - Built using Manifest v3, HTML, CSS, and JavaScript.
  - Popup interface with fields for hateful comment input, additional user input, and personalization options (e.g., target group/ally selection).
  - Display of generated CS suggestions with "edit" and "copy" functionality.
- **Backend:**

  - FastAPI + Uvicorn for API services.
  - Handles requests from the extension, orchestrates the retrieval and generation pipeline.
- **LLM Host & Model:**

  - Integration with Groq API hosting LlaMA 3 model for generating CS responses.
- **Retrieval Engine:**

  - Retrieves semantically similar examples from the CONAN dataset using an embedding encoder (SentenceTransformers via HuggingFaceEmbeddings).
  - Utilizes FAISS for vector storage and cosine similarity for semantic search.
- **Pipeline Implementation:**

  - Managed via LangChain to sequence data retrieval, prompt template construction, and LLM interaction.

**Functional Requirements (Prototype):**

1. User pastes a hateful comment into the browser extension's popup.
2. User provides optional additional input (ideas, text snippets, personal experiences).
3. User selects their role (target group member or ally) and may adjust further personalization options.
4. Upon clicking "Generate responses":
   - The comment and inputs are sent to the backend.
   - Backend retrieves five semantically similar CONAN examples.
   - The inputs and examples are merged into the prompt template.
   - The prompt is sent to the LLM via Groq API.
   - LLM returns three CS suggestions.
5. Suggestions are displayed to the user with individual "edit" and "copy" buttons.
6. User can copy and further post-edit the selected response before posting.

---

## Project Folder Hierarchy

The project follows a simple, high-level structure with clear separation between frontend and backend components:

```
project-root/
├── frontend/          # Browser extension
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.js
│   ├── popup.css
│   ├── content.js      # Content script (if needed)
│   └── assets/         # Icons, images, etc.
│
├── backend/            # FastAPI backend service
│   ├── main.py         # FastAPI app entry point
│   ├── routes/         # API route handlers
│   ├── models/         # Data models
│   ├── services/       # Business logic (retrieval, LLM calls)
│   ├── utils/          # Utility functions
│   ├── config.py       # Configuration management
│   └── requirements.txt
│
├── README.md           # Project documentation
└── project.md          # Technical development scope and setup guide
```

**Key Points:**

- **`frontend/`**: Contains all browser extension files (Manifest v3, HTML, CSS, JavaScript)
- **`backend/`**: Contains all backend Python code, organized into routes, models, services, and utilities
- **`README.md`**: Project documentation at the root level
- **`project.md`**: Technical development scope and setup guide
- All other files (`.gitignore`, `.env`, `venv/`) remain at the root but are not part of the core code structure

---

## Development Setup

### Dev System Setup

- **Operating System:** Windows
- **Python Version:** Python 3.14

### 1. Virtual Environment


Create and activate a Python virtual environment for the backend:

```bash
cd backend
py -3 -m venv .venv
.venv\Scripts\activate
```

Install backend dependencies (example `requirements.txt`):

- fastapi
- uvicorn
- langchain
- groq
- faiss
- sentence-transformers
- huggingface-hub

```bash
pip install -r requirements.txt
```

### 2. Running the Backend

```bash
cd backend
uvicorn main:app --reload
```

---

## Project Structure & Coding Practices

- **Modular Approach:**

  - Organize code into small, focused modules.
  - Each file should not exceed 500 lines (where possible) to improve readability, maintainability, and scalability.
  - Split logic into separate files for routes, models, utilities, components, etc.
- **Configuration Management:**

  - Use `.env` files for sensitive configuration (API keys, endpoints, etc.).
  - All secrets and environment-specific data must be loaded from `.env`.

---

## Creating a `.gitignore`

**Instructions:**

- Create a `.gitignore` file at the root of your project directory.
- **Essential entries:**
  - Python:
    - `.venv/`
    - `__pycache__/`
    - `*.pyc`
    - `.env`
  - Others as needed (e.g., `.DS_Store`, `.idea/`, `.vscode/`).

**Example `.gitignore`:**

```
# Python
.venv/
__pycache__/
*.pyc

# Environment
.env

# OS/File System
.DS_Store

# IDE
.idea/
.vscode/
```

---

## Creating a README

**Instructions:**

1. Create a `README.md` file at the root of your project directory.
2. Include the following sections:
   - Project Overview (summary from above)
   - Features & Functional Requirements
   - Technology Stack
   - Setup Instructions (virtual environment, installation, running backend/frontend)
   - Usage Instructions (how to use the extension)
  

**Example README structure:**

```markdown
# Human-AI Counter Speech Extension

## Overview
[Insert summary]

## Features
- [List functional requirements]


## Technology Stack
- [List stack]

## Setup
- [Copy setup instructions above]

## Usage
- [Describe how to use extension]
```
