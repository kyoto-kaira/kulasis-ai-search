# src/embedding/e5_embedder.py

from tqdm import tqdm
from typing import List

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer
from loguru import logger

from .base import BaseEmbedder


class E5Embedder(BaseEmbedder):
    """
    multilingual-e5-smallの埋め込みモデルを使用するクラス。
    """

    def __init__(self, model: str = "intfloat/multilingual-e5-small", batch_size: int = 16) -> None:
        self.model = model
        self.batch_size = batch_size
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")
        logger.info(f"Device: {self.device}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model)
        self.model = AutoModel.from_pretrained(self.model).to(self.device)

    def _embed(self, texts: List[str]) -> np.ndarray:
        """
        テキストリストをmultilingual-e5-smallの埋め込みモデルでベクトルに埋め込む。

        Parameters
        ----------
        texts : List[str]
            埋め込むテキストのリスト

        Returns
        -------
        np.ndarray
            埋め込みベクトルの配列
        """
        embeddings: List[np.ndarray] = []
        for i in tqdm(range(0, len(texts), self.batch_size)):
            batch_dict = self.tokenizer(
                texts[i : i + self.batch_size],
                max_length=512,
                padding=True,
                truncation=True,
                return_tensors="pt",
            )
            with torch.no_grad():
                outputs = self.model(**batch_dict.to(self.device))  # type: ignore
            embeddings.extend(
                self._average_pool(
                    outputs.last_hidden_state,
                    batch_dict["attention_mask"],
                )
                .cpu()
                .detach()
                .numpy()
            )

        return np.array(embeddings, dtype=np.float32)

    def _average_pool(self, last_hidden_states: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        """
        平均プーリングを行う関数。

        Parameters
        ----------
        last_hidden_states : torch.Tensor
            最終層の隠れ状態
        attention_mask : torch.Tensor
            アテンションマスク

        Returns
        -------
        torch.Tensor
            平均プーリングされたベクトル
        """
        last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
        return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

    def embed_passage(self, texts: List[str]) -> np.ndarray:
        """
        パッセージ(シラバステキスト)を埋め込む。
        文頭に"passage: "を付与して埋め込む。
        """
        return self._embed(["passage: " + text for text in texts])

    def embed_query(self, texts: List[str]) -> np.ndarray:
        """
        クエリを埋め込む。
        文頭に"query: "を付与して埋め込む。
        """
        return self._embed(["query: " + text for text in texts])
