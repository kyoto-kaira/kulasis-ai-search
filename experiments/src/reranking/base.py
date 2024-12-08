# src/reranking/base.py

from abc import ABC, abstractmethod
from typing import Dict, List


class BaseReranker(ABC):
    """
    リランキング機能の基底クラス
    """

    @abstractmethod
    def rerank(self, query: str, results: List[Dict]) -> List[Dict]:
        """
        リランキングを実行するメソッド。

        Parameters
        ----------
        query : str
            ユーザーのクエリ
        results : List[Dict]
            検索結果のリスト

        Returns
        -------
        List[Dict]
            リランキング後の検索結果のリスト
        """
        pass
