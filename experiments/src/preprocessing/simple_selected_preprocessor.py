# src/preprocessing/simple_selected_preprocessor.py

import re
from typing import Dict, List, Optional

from src.constants import ID_TO_LECTURE

from ..utils import SyllabusParser
from .base import BasePreprocessor


class SelectedPreprocessor(BasePreprocessor):
    """
    選別したテキスト前処理を行うクラス。
    """

    def __init__(self, chunk_size: int = 512, normalization: bool = True):
        self.chunk_size = chunk_size
        self.normalization = normalization

    def parse_html(self, html_content: str) -> Dict[str, Optional[str]]:
        """
        HTMLコンテンツをパースして、必要な情報を抽出する。

        Parameters
        ----------
        html_content : str
            HTMLコンテンツ

        Returns
        -------
        Dict[str, Optional[str]]
            パース結果の辞書
        """
        parser = SyllabusParser(html_content)
        data = parser.parse()
        return data

    def normalize_text(self, text: str) -> str:
        """
        テキストの正規化を行う。

        Parameters
        ----------
        text : str
            正規化前のテキスト

        Returns
        -------
        str
            正規化後のテキスト
        """
        text = re.sub(r"\s+", " ", text)
        text = text.replace("\u3000", " ")
        return text

    def chunk_text(self, text: str) -> List[str]:
        """
        テキストをチャンクに分割する。

        Parameters
        ----------
        text : str
            分割前のテキスト

        Returns
        -------
        List[str]
            チャンクに分割されたテキストのリスト
        """
        tokens = list(text)
        chunks = []
        for i in range(0, len(tokens), self.chunk_size):
            if len(tokens) - i < self.chunk_size:
                chunk = "".join(tokens[-self.chunk_size :])
                chunks.append(chunk)
            else:
                chunk = "".join(tokens[i : i + self.chunk_size])
                chunks.append(chunk)
        return chunks

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
                {"text_chunk": "...", "metadata": {"lecture_no": "...", ...}},
                {"text_chunk": "...", "metadata": {"lecture_no": "...", ...}},
                ...
            ]
        """
        processed_data = []
        for entry in data:

            html_content = entry.get("html_content", "")
            lecture_no = entry.get("lecture_no", "")
            lecture_info = ID_TO_LECTURE[lecture_no]
            parsed_content = self.parse_html(html_content)
            selected_list = [lecture_info["lecture_name"]]
            for k, v in parsed_content.items():
                if k in ["授業の概要・目的", "到達目標", "授業計画と内容"]:
                    selected_list.append(f"{k}: {v}")
            text = "\n".join(selected_list)

            if self.normalization:
                text = self.normalize_text(text)
            chunks = self.chunk_text(text)

            for chunk in chunks:
                processed_entry = {
                    "text_chunk": chunk,
                    "metadata": {
                        "lecture_no": lecture_no,
                        "lecture_name": lecture_info["lecture_name"],
                        "department": lecture_info["department"],
                        "section": lecture_info["section"],
                        "url": lecture_info["url"],
                    },
                }
                if isinstance(processed_entry["metadata"], dict):
                    processed_entry["metadata"].update(parsed_content)
                processed_data.append(processed_entry)

        return processed_data
