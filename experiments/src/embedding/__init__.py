# src/embedding/__init__.py

from .base import BaseEmbedder
from .gemini_embedder import GeminiEmbedder

__all__ = ["BaseEmbedder", "GeminiEmbedder"]
