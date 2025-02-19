# src/reranking/llm_reranker.py

import json
import os
from typing import Dict, List
from dotenv import load_dotenv
import cohere

from .base import BaseReranker

class CohereReranker(BaseReranker):
    """
    Cohereを用いたリランキングクラス。
    """

    def __init__(self, model: str, api_key: str = ""):
        load_dotenv()

        self.model = model
        self.api_key = api_key or os.getenv("COHERE_API_KEY")

        if not self.api_key:
            raise ValueError("OpenAI API key must be provided either via parameter or environment variable.")

        self.client = cohere.ClientV2(api_key=self.api_key)

    def rerank(self, query: str, results: List[Dict]) -> List[Dict]:
        """
        Geminiを用いて検索結果をリランキングする。

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
        # LLMにプロンプトを送信してスコアを取得
        docs = self.build_docs(results)
        reranked_results = self.client.rerank(
            model=self.model,
            query=query,
            documents=docs,
            top_n=len(docs),
        )
        # スコアを結果に追加してソート
        for reranked_result in reranked_results.results:
            results[reranked_result.index]["score"] = reranked_result.relevance_score
        sorted_results = sorted(results, key=lambda x: (x["score"],-x["distance"]), reverse=True)
        return sorted_results

    def build_docs(self,results: List[Dict]) -> List[str]:
        """
        metadataのresultsを、検索用のdocsに変換する。

        Parameters
        ----------
        query : str
            ユーザーのクエリ
        results : List[Dict]
            検索結果のリスト

        Returns
        -------
        str
            構築されたプロンプト
        """
        docs=[]
        for idx, result in enumerate(results, 1):
            lecture_name = result["metadata"]["lecture_name"]
            description = ", ".join(
                [f"{key}: {value}" for key, value in result["metadata"].items() if key != "lecture_no"]
            )
            doc=f"{idx}. 講義名: {lecture_name}\n   説明: {description}\n\n"
            docs.append(doc)
        return docs