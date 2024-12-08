# src/search/simple_search.py

from typing import Dict, List, Optional

import faiss
import numpy as np
from loguru import logger

from .base import BaseSearcher


class SimpleSearcher(BaseSearcher):
    """
    FAISSを用いたベクトル類似度検索クラス。
    """

    def __init__(self, index: faiss.Index, id_to_metadata: Dict):
        self.index = index
        self.id_to_metadata = id_to_metadata

        self.id_to_vector = {}
        for idx in range(self.index.ntotal):
            vector = np.zeros(self.index.d, dtype=np.float32)
            self.index.reconstruct(idx, vector)
            self.id_to_vector[str(idx)] = vector

    def search(self, query_vector: List[float], metadata_filter: Optional[Dict] = None, top_k: int = 10) -> List[Dict]:
        """
        クエリとのベクトル類似度に基づいた検索を行う。

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
        # フィルタリング
        filtered_ids = self.apply_metadata_filter(metadata_filter)
        if not filtered_ids:
            return []
        logger.info(f"Filtered: {self.index.ntotal} -> {len(filtered_ids)}")

        # フィルタ済みIDのベクトルを取得
        filtered_vectors = [self.id_to_vector[id_] for id_ in filtered_ids]

        # 一時的なFAISSインデックスを作成
        filtered_vectors_np = np.array(filtered_vectors).astype("float32")
        temp_index = faiss.IndexFlatL2(filtered_vectors_np.shape[1])
        temp_index.add(filtered_vectors_np)

        # クエリベクトルの整形
        query_np = np.array(query_vector).astype("float32").reshape(1, -1)

        # 類似度検索
        distances, indices = temp_index.search(query_np, top_k)

        # 検索結果の整形
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            actual_id = filtered_ids[idx]
            metadata = self.id_to_metadata.get(str(actual_id), {})
            results.append(
                {
                    "distance": float(distance),
                    "metadata": metadata,
                }
            )
        return results

    def apply_metadata_filter(self, filters: Optional[Dict]) -> List[str]:
        """
        メタデータによるフィルタリングを適用して、対象となるIDのリストを返す。

        Parameters
        ----------
        filters : Dict
            フィルタリング条件

        Returns
        -------
        List[str]
            フィルタ条件に合致するIDのリスト
        """
        if not filters:
            # フィルタが指定されていない場合は全IDを返す
            return list(self.id_to_metadata.keys())

        filtered_ids = []
        for id_, metadata in self.id_to_metadata.items():
            match = True
            for key, value in filters.items():
                if key == "曜時限":
                    for cond_weekday in value:
                        if cond_weekday in metadata.get("曜時限", value):
                            break
                    else:
                        match = False
                        break
                    break
                elif (key not in metadata) or (metadata[key] != value):
                    match = False
                    break
            if match:
                filtered_ids.append(id_)
        return filtered_ids
