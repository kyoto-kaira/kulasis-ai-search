# src/pipeline.py

import os
from typing import Dict, List, Tuple

import faiss
import numpy as np
from loguru import logger
from src.embedding import BaseEmbedder, E5Embedder
from src.preprocessing import BasePreprocessor, SelectedPreprocessor, SimplePreprocessor
from src.reranking import BaseReranker, BgeReranker
from src.search import SimpleSearcher
from src.utils import load_htmls_under_dir, load_json, save_json


class Piplines:
    def __init__(self, config: Dict) -> None:
        self.config = config

    def __call__(self) -> List[Dict]:
        index, processed_data, summary_data = self.pipeline_indexing()
        reranked_results_list = self.pipeline_search(index, processed_data, summary_data)

        return reranked_results_list

    @staticmethod
    def build_faiss_index(embeddings: np.ndarray) -> faiss.Index:
        """
        FAISSインデックスを構築する関数。

        Parameters
        ----------
        embeddings : np.ndarray
            埋め込みベクトルの配列

        Returns
        -------
        faiss.Index
            構築されたFAISSインデックス
        """
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)  # type: ignore
        return index

    def pipeline_indexing(self) -> Tuple[faiss.Index, List[Dict], List[str]]:
        """
        インデックス構築のパイプラインを実行する関数。

        Returns
        -------
        faiss.Index
            構築されたFAISSインデックス
        List[Dict]
            前処理済みデータ
        List[str]
            要約したデータ
        """
        index_dir = self.config["index"]["index_dir"]
        embedding_path = os.path.join(index_dir, self.config["index"]["embedding_name"])
        processed_data_path = os.path.join(index_dir, self.config["index"]["processed_data_name"])
        summarize_dir = self.config["summary"]["summary_dir"]
        summary_data_path = os.path.join(summarize_dir, self.config["summary"]["summary_name"])

        # すでに同名の前処理済みデータが存在する場合はそれをロード
        if os.path.exists(processed_data_path):
            processed_data = load_json(processed_data_path)
            logger.info(f"Loaded processed data from {processed_data_path}")
        else:
            # データロード
            raw_data = load_htmls_under_dir(self.config["data"]["input_dir"])
            logger.info(f"Loaded {len(raw_data)} records from {self.config['data']['input_dir']}")

            # 前処理
            preprocessor: BasePreprocessor
            if self.config["preprocessing"]["method"] == "simple":
                preprocessor = SimplePreprocessor(
                    chunk_size=self.config["preprocessing"]["chunk_size"],
                    normalization=self.config["preprocessing"]["normalization"],
                )
            elif self.config["preprocessing"]["method"] == "simple_selected":
                preprocessor = SelectedPreprocessor(
                    chunk_size=self.config["preprocessing"]["chunk_size"],
                    normalization=self.config["preprocessing"]["normalization"],
                )
            else:
                raise ValueError("Invalid preprocessing method")
            processed_data = preprocessor.run(raw_data)
            logger.info(f"Processed data into {len(processed_data)} chunks")

            # 前処理済みデータ保存
            os.makedirs(os.path.dirname(processed_data_path), exist_ok=True)
            save_json(processed_data, processed_data_path)
            logger.info(f"Saved processed data to {processed_data_path}")

        # すでに同名のインデックスファイルが存在する場合はそれをロード
        if os.path.exists(embedding_path):
            index = faiss.read_index(embedding_path)
            logger.info(f"Loaded FAISS index from {embedding_path}")
        else:
            # 埋め込み生成
            embedder = E5Embedder(
                model=self.config["embedding"]["model"],
                batch_size=self.config["embedding"]["batch_size"]
            )
            texts = [entry["text_chunk"] for entry in processed_data]
            embeddings = embedder.embed_passage(texts)
            logger.info(f"Generated embeddings with shape {embeddings.shape}")

            # FAISSインデックス構築
            index = self.build_faiss_index(embeddings)
            logger.info("Built FAISS index")

            # インデックス保存
            os.makedirs(os.path.dirname(embedding_path), exist_ok=True)
            faiss.write_index(index, embedding_path)
            logger.info(f"Saved FAISS index to {embedding_path}")

        # 要約したデータをロード
        if os.path.exists(summary_data_path):
            summary_data = load_json(summary_data_path)
            logger.info(f"Loaded summary data from {summary_data_path}")
        else:
            raise ValueError("Summary data does not exist.")

        return index, processed_data, summary_data

    def pipeline_search(self, index: faiss.Index, processed_data: list, summary_data: list) -> List[Dict]:
        # メタデータの準備
        id_to_metadata = {str(idx): entry["metadata"] for idx, entry in enumerate(processed_data)}

        # 要約をmetadataに追加する
        idx = 0
        lecture_no = ""
        for v in id_to_metadata.values():
            v["summary"] = summary_data[idx]
            lecture_no_ = v["lecture_no"]
            if lecture_no != lecture_no_:
                idx += 1
                lecture_no = lecture_no_

        logger.info("Prepared id to metadata mapping")

        # 検索システムの初期化
        searcher = SimpleSearcher(index=index, id_to_metadata=id_to_metadata)
        logger.info("Initialized Searcher")

        # リランキングシステムの初期化
        reranker: BaseReranker
        reranker = BgeReranker(model=self.config["reranking"]["model"])
        logger.info("Initialized Reranker")

        # 検索クエリの例
        embedder: BaseEmbedder
        embedder = E5Embedder(
            model=self.config["embedding"]["model"],
            batch_size=self.config["embedding"]["batch_size"]
        )
        queries = self.config["queries"]
        query_vector = embedder.embed_query(queries)
        logger.info("Encoded query")

        reranked_results_list = []
        for i, query in enumerate(queries):
            # 検索実行
            logger.info(f"===== Searching for: {query} =====")
            search_results = searcher.search(
                query_vector=query_vector[i].tolist(),
                metadata_filter=self.config["search"]["metadata_filter"],
                top_k=self.config["search"]["top_k"],
            )
            logger.info(f"Retrieved {len(search_results)} search results")

            # リランキング実行
            reranked_results = {"query": query}
            reranked_results["results"] = reranker.rerank(query=query, results=search_results)
            logger.info("Completed reranking:")
            for result in reranked_results["results"]:
                logger.debug(
                    f"  - {result['metadata']['lecture_name']} (score: {result['score']}, distance: {result['distance']})"
                )

            reranked_results_list.append(reranked_results)

        # 結果保存
        if "output_path" in self.config["data"]:
            os.makedirs(os.path.dirname(self.config["data"]["output_path"]), exist_ok=True)
            save_json(reranked_results_list, self.config["data"]["output_path"])
            logger.info(f"Saved reranked results to {self.config['data']['output_path']}")

        return reranked_results_list
