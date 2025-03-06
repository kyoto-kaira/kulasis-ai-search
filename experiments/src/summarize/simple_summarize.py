# src/summarize/simple_summarize.py

import json
import os
import re
from typing import Dict, List, Optional
import time

from dotenv import load_dotenv
from openai import OpenAI

from src.constants import ID_TO_LECTURE

from ..utils import SyllabusParser
from .base import BaseSummarizer


class SimpleSummarizer(BaseSummarizer):
    """
    Geminiを用いたリランキングクラス。
    """

    def __init__(self, model: str):
        load_dotenv()

        self.model = model
        self.api_key = os.getenv("OPEN_AI_API_KEY")

        if not self.api_key:
            raise ValueError("OpenAI API key must be provided either via parameter or environment variable.")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.openai.com/v1",
        )

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

    def batch_json_data(self, data: List[Dict]) -> List[Dict]:
        """
        バッチ処理のためのプロンプトの作成を行う。

        Parameters
        ----------
        text : str
            要約するテキスト

        Returns
        -------
        str
            バッチ処理のためのプロンプト
        """
        texts = []
        for entry in data:
            html_content = entry.get("html_content", "")
            lecture_no = entry.get("lecture_no", "")
            lecture_info = ID_TO_LECTURE[lecture_no]
            parsed_content = self.parse_html(html_content)
            text = "\n".join([f"{k}: {v}" for k, v in parsed_content.items()])
            text = self.normalize_text(text)
            text = "科目名は"+lecture_info["lecture_name"]+"。"+text
            texts.append(text)
    
        tasks = []

        for i in range(len(texts)):
            task = {
                "custom_id": f"task-{i}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "以下の文章を科目名、所属部局などを箇条書きで要約してください。"+texts[i]
                        }
                    ],
                }
            }

            tasks.append(task)
        return tasks

    def summarize(self, file_name: str) -> List[str]:
        """
        要約を実行する。

        Parameters
        ----------
        data : List[Dict]
            プロンプトのデータ。

        Returns
        -------
        List[str]
            要約したデータ。
        """
        
        batch_file = self.client.files.create(
            file=open(file_name, "rb"),
            purpose="batch"
            )
        batch_job = self.client.batches.create(
            input_file_id=batch_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h"
            )
        batch_job = self.client.batches.retrieve(batch_job.id)

        while batch_job.status != "completed":
            time.sleep(10)
            batch_job = self.client.batches.retrieve(batch_job.id)
            if batch_job.status == "failed":
                raise ValueError("Input file is too large or its format is wrong")

        result_file_id = batch_job.output_file_id
        result = self.client.files.content(result_file_id).content
        
        result_str = result.decode('utf-8')
        json_lines = result_str.splitlines()  

        results = []
        for line in json_lines: 
            json_object = json.loads(line)  
            results.append(json_object['response']['body']['choices'][0]['message']['content'])
        return results