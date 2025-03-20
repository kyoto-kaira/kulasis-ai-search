# src/embedding/base.py

from abc import ABC, abstractmethod
from typing import List

import numpy as np


class BaseEmbedder(ABC):
    """
    埋め込み生成の基底クラス
    """

    @abstractmethod
    def embed_passage(self, texts: List[str]) -> np.ndarray:
        """
        パッセージ(シラバステキスト)を埋め込む。

        Parameters
        ----------
        texts : List[str]
            埋め込むテキストのリスト

        Returns
        -------
        np.ndarray
            埋め込みベクトルの配列
        """
        pass

    @abstractmethod
    def embed_query(self, texts: List[str]) -> np.ndarray:
        """
        クエリを埋め込む。

        Parameters
        ----------
        texts : List[str]
            埋め込むテキストのリスト

        Returns
        -------
        np.ndarray
            埋め込みベクトルの配列
        """
        pass
