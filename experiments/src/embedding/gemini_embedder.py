# src/embedding/gemini_embedder.py

import os
from typing import List

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

from .base import BaseEmbedder


class GeminiEmbedder(BaseEmbedder):
    """
    Geminiの埋め込みモデルを使用するクラス。
    """

    def __init__(self, model: str, api_key: str = ""):
        load_dotenv()

        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key must be provided either via parameter or environment variable.")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/",
        )

    def embed_passage(self, texts: List[str]) -> np.ndarray:
        """
        テキストリストをGeminiの埋め込みモデルでベクトルに埋め込む。

        Parameters
        ----------
        texts : List[str]
            埋め込むテキストのリスト

        Returns
        -------
        np.ndarray
            埋め込みベクトルの配列
        """
        # 1バッチ=100個
        embeddings = []
        for i in range(0, len(texts), 100):
            response = self.client.embeddings.create(
                model=self.model,
                input=texts[i : i + 100],
                encoding_format="float",
            )
            embeddings.extend([item.embedding for item in response.data])
        return np.array(embeddings, dtype=np.float32)

    def embed_query(self, texts: List[str]) -> np.ndarray:
        # クエリの埋め込みはパッセージの埋め込みと同じ
        return self.embed_passage(texts)
