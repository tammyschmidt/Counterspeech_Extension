"""Retrieval service for CONAN dataset using FAISS."""

import csv
import logging
from pathlib import Path
from typing import Dict, List, Optional

from langchain_core.documents import Document
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS

from config import (
    CONAN_DATA_PATH,
    EMBEDDING_MODEL_NAME,
    RETRIEVAL_TOP_K,
    FAISS_INDEX_PATH,
)

logger = logging.getLogger(__name__)


class RetrievalService:
    """Loads the CONAN dataset and exposes a similarity retriever."""

    def __init__(
        self,
        data_path: str = CONAN_DATA_PATH,
        embedding_model_name: str = EMBEDDING_MODEL_NAME,
        default_k: int = RETRIEVAL_TOP_K,
        persist_path: str = FAISS_INDEX_PATH,
    ):
        self.data_path = Path(data_path)
        self.embedding_model_name = embedding_model_name
        self.default_k = default_k
        self.persist_path = Path(persist_path)

        if not self.data_path.exists():
            raise FileNotFoundError(
                f"CONAN dataset not found at {self.data_path}. "
                "Please ensure the CSV is available."
            )

        self.embedding_model = SentenceTransformerEmbeddings(
            model_name=self.embedding_model_name
        )

        if self.persist_path.exists():
            logger.info(
                "Loading cached FAISS index from %s with embedding model %s.",
                self.persist_path,
                self.embedding_model_name,
            )
            self.vector_store = FAISS.load_local(
                str(self.persist_path),
                self.embedding_model,
                allow_dangerous_deserialization=True,
            )
            self.doc_count = self.vector_store.index.ntotal
            logger.info("Loaded FAISS index containing %d documents.", self.doc_count)
        else:
            logger.info("No existing FAISS index found. Building from CSV at %s.", self.data_path)
            examples = self._load_dataset()

            logger.info(
                "Loaded %d CONAN examples. Building embedding index with %s.",
                len(examples),
                self.embedding_model_name,
            )
            self.vector_store = self._build_vector_store(examples)
            self.doc_count = len(examples)
            self._persist_index()

    def _load_dataset(self) -> List[Dict[str, str]]:
        """Load the CONAN dataset from CSV."""
        examples: List[Dict[str, str]] = []

        with self.data_path.open(encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            required_fields = {"HATE_SPEECH", "COUNTER_NARRATIVE"}
            missing_fields = required_fields.difference(reader.fieldnames or [])
            if missing_fields:
                raise ValueError(
                    f"CSV is missing required columns: {', '.join(sorted(missing_fields))}"
                )

            for row in reader:
                hate_speech = (row.get("HATE_SPEECH") or "").strip()
                counter_narrative = (row.get("COUNTER_NARRATIVE") or "").strip()

                if not hate_speech or not counter_narrative:
                    continue

                example = {
                    "hate_speech": hate_speech,
                    "counter_narrative": counter_narrative,
                    "target": (row.get("TARGET") or "").strip(),
                    "version": (row.get("VERSION") or "").strip(),
                }
                examples.append(example)

        if not examples:
            raise ValueError("No valid CONAN examples were loaded from the CSV.")

        return examples

    def _build_vector_store(self, examples: List[Dict[str, str]]) -> FAISS:
        """Build the FAISS index from the loaded examples."""
        documents = [
            Document(
                page_content=example["hate_speech"],
                metadata={
                    "counter_narrative": example["counter_narrative"],
                    "target": example["target"],
                    "version": example["version"],
                },
            )
            for example in examples
        ]

        return FAISS.from_documents(documents, self.embedding_model)

    def _persist_index(self) -> None:
        """Persist the FAISS index locally for faster subsequent loads."""
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info("Saving FAISS index to %s", self.persist_path)
        self.vector_store.save_local(str(self.persist_path))

    def get_similar_examples(
        self, hateful_comment: str, top_k: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """Return the most similar CONAN examples for a hateful comment."""
        if not hateful_comment or not hateful_comment.strip():
            return []

        k = top_k or self.default_k
        docs = self.vector_store.similarity_search(hateful_comment, k=k)

        return [
            {
                "hate_speech": doc.page_content,
                "counter_narrative": doc.metadata.get("counter_narrative", ""),
                "target": doc.metadata.get("target", ""),
                "version": doc.metadata.get("version", ""),
            }
            for doc in docs
        ]

