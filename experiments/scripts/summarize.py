import json
import os
import re
import sys
import time
from typing import Dict, List, Optional

from dotenv import load_dotenv
from loguru import logger
from openai import OpenAI

sys.path.append(os.getcwd())

from src.constants import ID_TO_LECTURE
from src.utils import SyllabusParser, load_htmls_under_dir, save_json, save_list_json


def parse_html(html_content: str) -> Dict[str, Optional[str]]:
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


def normalize_text(text: str) -> str:
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


def batch_json_data(model: str, data: List[Dict]) -> List[Dict]:
    """
    バッチ処理のためのプロンプトの作成を行う。

    Parameters
    ----------
    model : str
        モデル名

    data : List[Dict]
        要約するテキスト

    Returns
    -------
    List[Dict]
        バッチ処理のためのプロンプト
    """
    texts = []
    for entry in data:
        html_content = entry.get("html_content", "")
        lecture_no = entry.get("lecture_no", "")
        lecture_info = ID_TO_LECTURE[lecture_no]
        parsed_content = parse_html(html_content)
        text = "\n".join([f"{k}: {v}" for k, v in parsed_content.items()])
        text = normalize_text(text)
        text = "科目名は" + lecture_info["lecture_name"] + "。" + text
        texts.append(text)

    tasks = []

    for i in range(len(texts)):
        task = {
            "custom_id": f"task-{i}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "以下の文章を科目名、所属部局などを箇条書きで要約してください。" + texts[i],
                    }
                ],
            },
        }

        tasks.append(task)
    return tasks


def summarize(file_name: str) -> List[str]:
    """
    要約を実行する。

    Parameters
    ----------
    file_name : str
        プロンプトのデータ。
    Returns
    -------
    List[str]
        要約したデータ。
    """
    load_dotenv()

    api_key = os.getenv("OPEN_AI_API_KEY")

    if not api_key:
        raise ValueError("OpenAI API key must be provided either via parameter or environment variable.")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.openai.com/v1",
    )
    batch_file = client.files.create(file=open(file_name, "rb"), purpose="batch")
    batch_job = client.batches.create(
        input_file_id=batch_file.id, endpoint="/v1/chat/completions", completion_window="24h"
    )
    batch_job = client.batches.retrieve(batch_job.id)

    while batch_job.status != "completed":
        time.sleep(10)
        batch_job = client.batches.retrieve(batch_job.id)
        if batch_job.status == "failed":
            raise ValueError("Input file is too large or its format is wrong")

    result_file_id = batch_job.output_file_id
    if result_file_id == None:
        ValueError("result_file_id is None")
    else:
        result = client.files.content(result_file_id).content

    result_str = result.decode("utf-8")
    json_lines = result_str.splitlines()

    results = []
    for line in json_lines:
        json_object = json.loads(line)
        results.append(json_object["response"]["body"]["choices"][0]["message"]["content"])
    return results


summary_data_path = os.path.join("data/summary", "summary_data.json")
model = "gpt-4o-mini"

raw_data = load_htmls_under_dir("data/raw")
logger.info(f"Loaded {len(raw_data)} records from data/raw")

sammary_data = []
for i in range(0, len(raw_data), 3000):
    prompt_data_path = os.path.join("data/summary", f"summary_prompt{i//3000+1}.json")
    if not os.path.exists(prompt_data_path):
        # プロンプトデータ保存
        prompt_data = batch_json_data(model, raw_data[i : i + 3000])
        os.makedirs(os.path.dirname(prompt_data_path), exist_ok=True)
        save_list_json(prompt_data, prompt_data_path)
        logger.info(f"Saved prompt data to {prompt_data_path}")

    # 要約データ保存
    sammary_data.extend(summarize(prompt_data_path))
os.makedirs(os.path.dirname(summary_data_path), exist_ok=True)
save_json(sammary_data, summary_data_path)
logger.info(f"Saved summary data to {summary_data_path}")
