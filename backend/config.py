# Configuration management
# Loads environment variables from .env file

import os
from pathlib import Path
from dotenv import load_dotenv

# Get the project root directory (parent of backend directory)
backend_dir = Path(__file__).parent
project_root = backend_dir.parent

# Load environment variables from .env file in project root
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")  # Default model

# Retrieval / Dataset configuration
DATA_DIR = backend_dir / "data"
CONAN_DATA_PATH = os.getenv(
    "CONAN_DATA_PATH",
    str(DATA_DIR / "Multitarget-CONAN.csv")
)
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "all-mpnet-base-v2"
)
RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "5"))
FAISS_INDEX_PATH = os.getenv(
    "FAISS_INDEX_PATH",
    str(DATA_DIR / "faiss_index")
)

# API Configuration
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))

# CORS Configuration
CORS_ORIGINS = [origin.strip() for origin in os.getenv(
    "CORS_ORIGINS",
    "chrome-extension://iipmkpjomfpgimolapcoibedkikienoh,http://127.0.0.1:5173"
).split(",") if origin.strip()]
CORS_ORIGIN_REGEX = os.getenv("CORS_ORIGIN_REGEX", r"chrome-extension://.*")

# Validate required environment variables
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set. Please add it to your .env file.")
