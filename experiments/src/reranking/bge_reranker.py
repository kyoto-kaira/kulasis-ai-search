# src/reranking/llm_reranker.py

from typing import Dict, List

from sentence_transformers import SentenceTransformer

from .base import BaseReranker


class BgeReranker(BaseReranker):
    """
    Cohereを用いたリランキングクラス。
    """

    def __init__(self, model: str):
        self.model = SentenceTransformer(model)

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
        documents = self.build_documents(results)
        scores = self.calculate_rerank_scores(
            query=query,
            documents=documents,
        )

        # スコアを結果に追加してソート
        for result, score in zip(results, scores):
            result["score"] = score
        sorted_results = sorted(results, key=lambda x: (x["score"], -x["distance"]), reverse=True)
        return sorted_results

    def build_documents(self, results: List[Dict]) -> List[str]:
        """
        metadataのresultsを、検索用のdocumentsに変換する。

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
        documents = []
        for idx, result in enumerate(results, 1):
            lecture_name = result["metadata"]["lecture_name"]
            description = ", ".join(
                [f"{key}: {value}" for key, value in result["metadata"].items() if key != "lecture_no"]
            )
            document = f"{idx}. 講義名: {lecture_name}\n   説明: {description}\n\n"
            documents.append(document)
        return documents

    def calculate_rerank_scores(self, query: str, documents: list[str]) -> List[float]:
        """
        rerankスコアを計算する。

        Parameters
        ----------
        query : str
            ユーザーのクエリ
        documents : list[str]
            検索結果のリスト

        Returns
        -------
        List[Dict]
            リランキング後の検索結果のリスト
        """
        q_embeddings = self.model.encode([query], normalize_embeddings=True)
        p_embeddings = self.model.encode(documents, normalize_embeddings=True)
        rerank_scores = q_embeddings @ p_embeddings.T
        return list(map(float, rerank_scores[0].tolist()))
