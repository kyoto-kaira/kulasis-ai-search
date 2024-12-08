# src/utils/io.py

import json
import pickle
from pathlib import Path
from typing import Any, Dict, List


def load_htmls_under_dir(dir_path: str) -> List[Dict]:
    """
    ディレクトリ内およびサブディレクトリ内のHTMLファイルを読み込む関数。

    Parameters
    ----------
    dir_path : str
        HTMLファイルが格納されているディレクトリのパス

    Returns
    -------
    List[Dict]
        ファイル名とHTMLコンテンツの辞書のリスト
        [
            {"html_content": "<html>...</html>", "lecture_no": "12345"},
            {"html_content": "<html>...</html>", "lecture_no": "12346"},
        ]
    """
    html_files = []
    path = Path(dir_path)
    for file_path in path.rglob("*.html"):
        try:
            html_content = file_path.read_text(encoding="utf-8")
            lecture_no = file_path.stem
            html_files.append(
                {
                    "html_content": html_content,
                    "lecture_no": lecture_no,
                }
            )
        except Exception as e:
            print(f"Failed to read {file_path}: {e}")
    return html_files


def load_json(path: str) -> Any:
    """
    JSONファイルを読み込む関数。

    Parameters
    ----------
    path : str
        読み込むJSONファイルのパス

    Returns
    -------
    Any
        JSONデータ
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_pickle(path: str) -> Any:
    """
    Pickleファイルを読み込む関数。

    Parameters
    ----------
    path : str
        読み込むPickleファイルのパス

    Returns
    -------
    Any
        Pickleデータ
    """
    with open(path, "rb") as f:
        return pickle.load(f)


def save_json(data: Any, path: str) -> None:
    """
    JSONファイルにデータを書き込む関数。

    Parameters
    ----------
    data : Any
        書き込むデータ
    path : str
        書き込む先のJSONファイルのパス
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def save_pickle(data: Any, path: str) -> None:
    """
    Pickleファイルにデータを書き込む関数。

    Parameters
    ----------
    data : Any
        書き込むデータ
    path : str
        書き込む先のPickleファイルのパス
    """
    with open(path, "wb") as f:
        pickle.dump(data, f)
