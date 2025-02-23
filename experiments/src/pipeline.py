# src/pipeline.py

import os
from typing import Dict, List, Tuple

import faiss
import numpy as np
from loguru import logger
from src.embedding import GeminiEmbedder
from src.preprocessing import SimplePreprocessor,SimpleSelectedPreprocessor
from src.reranking import GeminiReranker
from src.search import SimpleSearcher
from src.utils import load_htmls_under_dir, load_json, save_json


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
    index.add(embeddings)
    return index


def pipeline_indexing(config: Dict) -> Tuple[faiss.Index, List[Dict]]:
    """
    インデックス構築のパイプラインを実行する関数。

    Parameters
    ----------
    config : Dict
        設定

    Returns
    -------
    faiss.Index
        構築されたFAISSインデックス
    List[Dict]
        前処理済みデータ
    """
    index_dir = config["index"]["index_dir"]
    embedding_path = os.path.join(index_dir, config["index"]["embedding_name"])
    processed_data_path = os.path.join(index_dir, config["index"]["processed_data_name"])

    # すでに同名の前処理済みデータが存在する場合はそれをロード
    if os.path.exists(processed_data_path):
        processed_data = load_json(processed_data_path)
        logger.info(f"Loaded processed data from {processed_data_path}")
    else:
        # データロード
        raw_data = load_htmls_under_dir(config["data"]["input_dir"])
        logger.info(f"Loaded {len(raw_data)} records from {config['data']['input_dir']}")

        # 前処理
        if config["preprocessing"]["method"] == "simple":
            preprocessor = SimplePreprocessor(
                chunk_size=config["preprocessing"]["chunk_size"],
                normalization=config["preprocessing"]["normalization"],
            )
        if config["preprocessing"]["method"] == "simple_selected":
            preprocessor = SimpleSelectedPreprocessor(
                chunk_size=config["preprocessing"]["chunk_size"],
                normalization=config["preprocessing"]["normalization"],
            )        
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
        if config["embedding"]["method"] == "gemini":
            embedder = GeminiEmbedder(model=config["embedding"]["model"])
        texts = [entry["text_chunk"] for entry in processed_data]
        embeddings = embedder.embed_passage(texts)
        logger.info(f"Generated embeddings with shape {embeddings.shape}")

        # FAISSインデックス構築
        index = build_faiss_index(embeddings)
        logger.info("Built FAISS index")

        # インデックス保存
        os.makedirs(os.path.dirname(embedding_path), exist_ok=True)
        faiss.write_index(index, embedding_path)
        logger.info(f"Saved FAISS index to {embedding_path}")

    return index, processed_data


def pipeline_search(config: Dict, index: faiss.Index, processed_data: list) -> List[Dict]:
    # メタデータの準備
    id_to_metadata = {str(idx): entry["metadata"] for idx, entry in enumerate(processed_data)}
    logger.info("Prepared id to metadata mapping")

    # 検索システムの初期化
    if config["search"]["method"] == "simple":
        searcher = SimpleSearcher(index=index, id_to_metadata=id_to_metadata)
    logger.info("Initialized Searcher")

    # リランキングシステムの初期化
    if config["reranking"]["method"] == "gemini":
        reranker = GeminiReranker(model=config["reranking"]["model"])
    logger.info("Initialized Reranker")

    # 検索クエリの例
    if config["embedding"]["method"] == "gemini":
        embedder = GeminiEmbedder(model=config["embedding"]["model"])
    queries = config["queries"]
    query_vector = embedder.embed_query(queries)
    logger.info("Encoded query")

    reranked_results_list = []
    for i, query in enumerate(queries):
        # 検索実行
        logger.info(f"===== Searching for: {query} =====")
        search_results = searcher.search(
            query_vector=query_vector[i].tolist(),
            metadata_filter=config["search"]["metadata_filter"],
            top_k=config["search"]["top_k"],
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
    if "output_path" in config["data"]:
        os.makedirs(os.path.dirname(config["data"]["output_path"]), exist_ok=True)
        save_json(reranked_results_list, config["data"]["output_path"])
        logger.info(f"Saved reranked results to {config['data']['output_path']}")

    return reranked_results_list


def main(config: Dict) -> List[Dict]:
    # インデックス構築
    index, processed_data = pipeline_indexing(config)

    # 検索
    reranked_results_list = pipeline_search(config, index, processed_data)

    return reranked_results_list
