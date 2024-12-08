# src/run_experiment.py

import os
import shutil
import sys
import uuid
from datetime import datetime

import weave
import yaml
from loguru import logger
from src.pipeline import main
from src.utils import load_json


def run_experiment(config_path: str, experiment_name: str = "default_experiment") -> None:
    """
    実験を実行し、結果を保存する関数。

    Parameters
    ----------
    config_path : str
        使用する設定ファイルのパス
    experiment_name : str, optional
        実験名, by default "default_experiment"
    """
    logger.info(f"Starting experiment '{experiment_name}' with config '{config_path}'")

    # 実験IDの生成
    experiment_id = f"{experiment_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    results_dir = os.path.join("results", experiment_id)
    os.makedirs(results_dir, exist_ok=True)
    logger.info(f"Results will be saved to '{results_dir}'")

    # 設定ファイルのロード
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 設定ファイルのコピーを保存
    shutil.copy(config_path, os.path.join(results_dir, "config_used.yaml"))
    logger.info("Copied config file to results directory")

    # パイプラインの実行
    config["data"]["output_path"] = os.path.join(results_dir, "reranked_results.json")
    main(config)

    # weaveへの記録
    @weave.op()
    def push_to_weave(query: str) -> str:
        """weaveにデータを送信する用の関数。"""
        result_msg = "| 講義名 | distance | score |\n| --- | --- | --- |\n"
        for result in results["results"]:
            lecture_name = result["metadata"]["lecture_name"]
            url = result["metadata"]["url"]
            distance = result["distance"]
            score = result["score"]
            result_msg += f"| [{lecture_name}]({url}) | {distance} | {score} |\n"

        return result_msg

    weave.init(config["wandb"]["project"])
    results_list = load_json(config["data"]["output_path"])
    for results in results_list:
        query = results["query"]
        push_to_weave(query=query)

    logger.info(f"Experiment '{experiment_id}' completed successfully.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_experiment.py <config_path> [experiment_name]")
        sys.exit(1)

    config_path = sys.argv[1]
    experiment_name = sys.argv[2] if len(sys.argv) > 2 else "default_experiment"

    run_experiment(config_path, experiment_name)
