from typing import Any, Dict

import streamlit as st
from src.constants import (
    ACADEMIC_FIELDS,
    CLASS_TYPES,
    DEPARTMENTS,
    EMPTY_OPTION,
    LANGUAGES,
    LEVELS,
    SECTION_STRUCTURE,
    SEMESTERS,
)
from src.pipeline import main


def run_search(
    search_sentence: str,
    selected_department: str,
    selected_section: str,
    selected_class_type: str,
    selected_language: str,
    selected_semester: str,
    selected_level: str,
    selected_academic_field: str,
    search_teacher: str,
    selected_weekdays: dict,
) -> dict:
    """
    授業検索を実行する関数。

    Parameters
    ----------
    search_sentence : str
        AI検索用の自由入力テキスト。例: 「Pythonでプログラミングを学びたい」
    selected_department : str
        学部名。例: 「工学部」「全学共通科目」
    selected_section : str
        学科名または専攻名。例: 「情報学科」
    selected_class_type : str
        授業形態。例: 「講義」「実習」
    selected_language : str
        使用言語。例: 「日本語」「英語」
    selected_semester : str
        開講期（学期）。例: 「前期」「後期」
    selected_level : str
        授業の難易度や対象レベル。例: 「導入的な内容の科目（学部科目）」
    selected_academic_field : str
        学問分野。例: 「情報学基礎」「デザイン学」
    search_teacher : str
        教員名。例: 「山田太郎」
    selected_weekdays : dict
        曜日と時限の指定。以下の形式の辞書で渡す必要がある。
        {
            "月1": True,
            "月2": False,
            ...
            "集中": True,
        }

    Returns
    -------
    dict
        検索結果を辞書形式で返す。結果は以下の形式を持つ。
        {
            "query": str,
            "results": [
                {"distance": float, "score": float, "metadata": dict},
                ...
            ]
        }
    """
    # config.yamlと同形式
    config: Dict[str, Any] = {
        "data": {"input_dir": "data/raw"},
        "index": {
            "index_dir": "data/index_selected",
            "embedding_name": "faiss_index.bin",
            "processed_data_name": "processed_data.json",
        },
        "preprocessing": {"method": "simple_selected", "chunk_size": 2048, "normalization": True},
        "embedding": {"method": "e5", "model": "intfloat/multilingual-e5-small", "batch_size": 32},
        "search": {
            "method": "simple",
            "metadata_filter": {},
            "top_k": 10,
        },
        "reranking": {"method": "gemini", "model": "gemini-1.5-flash"},
        "summarize": {"summary_output": True, "model": "gpt-4o-mini", "summarize_dir": "data/summary", "summary_name": "summary_data.json"},

        "queries": None,
    }

    config["queries"] = [search_sentence]
    metadata_filter = {
        "department": selected_department,
        "section": selected_section,
        "授業形態": selected_class_type,
        "使用言語": selected_language,
        "開講年度・開講期": selected_semester,
        "レベル": selected_level,
        "学問分野": selected_academic_field,
        "氏名": search_teacher,
        "曜時限": [weekday for weekday, flag in selected_weekdays.items() if flag],
    }
    if search_teacher == "":
        del metadata_filter["氏名"]
    metadata_filter = {k: v for k, v in metadata_filter.items() if v != EMPTY_OPTION}
    config["search"]["metadata_filter"] = metadata_filter

    reranked_results_list = main(config)

    return reranked_results_list[0]


# ページの設定
st.set_page_config(
    page_title="KULASIS講義検索 with AI",
    page_icon="🔍",
)
st.title("KULASIS講義検索 with AI")

# 検索フォーム
search_sentence = st.text_area("AI検索", placeholder="探したい講義の特徴を自由に入力してください")

selected_department = st.selectbox("学部", [EMPTY_OPTION] + DEPARTMENTS)
if selected_department != EMPTY_OPTION:
    selected_section: str = st.selectbox("学科等", [EMPTY_OPTION] + SECTION_STRUCTURE[selected_department])
else:
    selected_section = st.selectbox("学科等", [EMPTY_OPTION])

selected_class_type = st.selectbox("授業形態", [EMPTY_OPTION] + CLASS_TYPES)

selected_language = st.selectbox("使用言語", [EMPTY_OPTION] + LANGUAGES)

selected_semester = st.selectbox("開講期", [EMPTY_OPTION] + SEMESTERS)

selected_level = st.selectbox("レベル", [EMPTY_OPTION] + LEVELS)

selected_academic_field = st.selectbox("学問分野", [EMPTY_OPTION] + ACADEMIC_FIELDS)

search_teacher = st.text_input("教員名")

st.write("曜時限")
mon, tue, wed, thu, fri = st.columns(5)
weekdays = ["月", "火", "水", "木", "金"]
weekdays_columns = [mon, tue, wed, thu, fri]
selected_weekdays = {}
for i, day in enumerate(weekdays):
    for j in range(5):
        key = f"{day}{j+1}"
        selected_weekdays[key] = weekdays_columns[i].checkbox(key, value=True, key=key)
selected_weekdays["集中講義"] = st.checkbox("集中講義", value=True, key="集中講義")

# 検索実行
if st.button("検索"):
    st.divider()
    with st.spinner("検索中..."):
        search_result = run_search(
            search_sentence=search_sentence,
            selected_department=selected_department,
            selected_section=selected_section,
            selected_class_type=selected_class_type,
            selected_language=selected_language,
            selected_semester=selected_semester,
            selected_level=selected_level,
            selected_academic_field=selected_academic_field,
            search_teacher=search_teacher,
            selected_weekdays=selected_weekdays,
        )

    expanders = []
    for lecture in search_result["results"]:
        lecture_name = lecture["metadata"]["lecture_name"]
        score = lecture["score"]
        distance = lecture["distance"]
        expanders.append(st.expander(f"**{lecture_name}** (スコア: {score}, 距離: {distance})"))
        for key, value in lecture["metadata"].items():
            expanders[-1].markdown(f"**{key}**")
            expanders[-1].markdown(value)
