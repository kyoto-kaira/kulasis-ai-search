# src/search/base.py

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseSearcher(ABC):
    """
    検索機能の基底クラス
    """

    @abstractmethod
    def search(self, query_vector: List[float], metadata_filter: Optional[Dict] = None, top_k: int = 10) -> List[Dict]:
        """
        検索を実行するメソッド。

        Parameters
        ----------
        query_vector : List[float]
            クエリの埋め込みベクトル
        metadata_filter : Dict, optional
            メタデータによるフィルタリング条件
        top_k : int
            取得する上位K件

        Returns
        -------
        List[Dict]
            検索結果のリスト
        """
        pass
