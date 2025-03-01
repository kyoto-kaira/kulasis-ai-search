# src/reranking/llm_reranker.py

import json
import os
from typing import Dict, List

from dotenv import load_dotenv
from openai import OpenAI

from .base import BaseReranker


class GeminiReranker(BaseReranker):
    """
    Geminiを用いたリランキングクラス。
    """

    def __init__(self, model: str, api_key: str = ""):
        load_dotenv()

        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("OpenAI API key must be provided either via parameter or environment variable.")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/",
        )

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
        prompt = self.build_prompt(query, results)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        scores = self.parse_response(str(response.choices[0].message.content))

        # スコアを結果に追加してソート
        for result, score in zip(results, scores):
            result["score"] = score
        sorted_results = sorted(results, key=lambda x: (x["score"], -x["distance"]), reverse=True)
        return sorted_results

    def build_prompt(self, query: str, results: List[Dict]) -> str:
        """
        LLMへのプロンプトを構築する。

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
        prompt = ""
        for idx, result in enumerate(results, 1):
            lecture_name = result["metadata"]["lecture_name"]
            description = ", ".join(
                [f"{key}: {value}" for key, value in result["metadata"].items() if key != "lecture_no"]
            )
            prompt += f"{idx}. 講義名: {lecture_name}\n   説明: {description}\n\n"
        prompt += (
            f"上記の講義について、ユーザーのクエリ '{query}' に対する関連度スコアを1から10で評価してください。\n"
            "関連度スコア(1~10)を以下のJSON形式(Dict[str, List[int]])で返してください。\n{'scores': [score, ...]}"
        )
        return prompt

    def parse_response(self, response_text: str) -> List[float]:
        """
        LLMのレスポンスをパースしてスコアを抽出する。

        Parameters
        ----------
        response_text : str
            LLMからのレスポンステキスト

        Returns
        -------
        List[float]
            抽出されたスコアのリスト
        """
        scores = json.loads(response_text)
        scores_list = [float(score) for score in scores["scores"]]
        return scores_list
