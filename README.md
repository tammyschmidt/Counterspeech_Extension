# Human-AI Counter Speech Extension

## Overview
This project will develop a browser extension to facilitate human-AI collaboration in countering online hate speech (HS) through effective and authentic counter speech (CS). The extension aims to lower barriers to engagement—such as limited time, emotional strain, and uncertainty about how to respond—by providing users with AI-generated CS suggestions that they can personalize. The system leverages a state-of-the-art language model, a retrieval engine, and embedding technologies to generate contextually relevant and impactful responses. The ultimate goal is to empower individuals, whether targets or allies, to participate constructively in online discourse.

## Features
- [List functional requirements]

## Technology Stack
- [List stack]

## Setup
- Backend:
  - `cd backend`
  - Create and activate a virtualenv (optional for local dev)
  - `pip install -r requirements.txt`
  - `uvicorn main:app --reload`
- Frontend:
  - Load the `frontend` folder as an unpacked extension in your browser (Manifest v3).

## Deployment on Railway (no Docker)

- **What Railway will detect**
  - Root `requirements.txt` (which includes `backend/requirements.txt`).
  - `runtime.txt`
  - `Procfile`


- **Steps**
  - Push this repository to GitHub (or another Git provider supported by Railway).
  - Create a new **Service** in Railway and link it to this repo.
  - Railway will:
    - Install Python 3.11.
    - Install dependencies from `requirements.txt`.
    - Use the `Procfile` to start the app on the correct `$PORT`.

- **Environment variables (required)**
  - Set these in the Railway service settings:
    - `GROQ_API_KEY`: your Groq API key.
  - Optional overrides (if you need them):
    - `GROQ_MODEL` (defaults to `llama-3.1-70b-versatile`)
    - `CONAN_DATA_PATH`, `EMBEDDING_MODEL_NAME`, `RETRIEVAL_TOP_K`, `FAISS_INDEX_PATH`

- **API endpoints**
  - Root: `GET /` → basic info and link to docs.
  - Health check: `GET /api/health`
  - Generate counter speech: `POST /api/generate`

## Usage
- [Describe how to use extension]

