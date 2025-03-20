# src/preprocessing/base.py

from abc import ABC, abstractmethod
from typing import Dict, List


class BasePreprocessor(ABC):
    """
    前処理の基底クラス
    """

    @abstractmethod
    def run(self, data: List[Dict]) -> List[Dict]:
        """
        前処理を実行する。

        Parameters
        ----------
        data : List[Dict]
            前処理対象のデータ。以下の形式を持つ。
            [
                {"html_content": "...", "lecture_no": "..."},
                {"html_content": "...", "lecture_no": "..."},
                ...
            ]

        Returns
        -------
        List[Dict]
            前処理後のデータ。結果は以下の形式を持つ。
            [
                {"text": "...", "metadata": {"lecture_no": "...", ...}},
                {"text": "...", "metadata": {"lecture_no": "...", ...}},
                ...
            ]
        """
        pass
