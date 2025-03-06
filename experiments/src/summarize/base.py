# src/summarize/base.py

from abc import ABC, abstractmethod
from typing import Dict, List


class BaseSummarizer(ABC):
    """
    要約機能の基底クラス
    """

    @abstractmethod
    def summarize(self, query: str, results: List[Dict]) -> List[Dict]:
        """
        要約を実行するメソッド。

        Parameters
        ----------
        query : str
            ユーザーのクエリ
        results : List[Dict]
            検索結果のリスト

        Returns
        -------
        List[Dict]
            要約後の検索結果のリスト
        """
        pass
