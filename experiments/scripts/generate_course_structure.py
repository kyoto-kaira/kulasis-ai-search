import json
from typing import Dict, List


def get_section_structure(path_to_json: str) -> Dict[str, List[str]]:
    """
    courses.jsonから「学科等」の構造情報を取得する

    Parameters
    ----------
    path_to_json : str
        courses.jsonのパス

    Returns
    -------
    Dict[str, List[str]]
        「学科等」の構造情報
    """
    with open(path_to_json, "r", encoding="utf-8") as f:
        courses = json.load(f)
    section_structure = {}
    for department, sections in courses.items():
        section_structure[department] = list(sections.keys())
    return section_structure


if __name__ == "__main__":
    section_structure = get_section_structure("data/courses.json")
    with open("data/section_structure.json", "w", encoding="utf-8") as f:
        json.dump(section_structure, f, ensure_ascii=False, indent=4)
