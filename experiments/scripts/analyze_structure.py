# 学部>学科等>講義の構造を解析するスクリプト
import json

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from .common import get_lecture_no

base_url = "https://www.k.kyoto-u.ac.jp/external/open_syllabus/"

# ページを取得
response = requests.get(base_url + "all")
response.raise_for_status()
content = response.content
html_content = content.decode("CP932")
soup = BeautifulSoup(html_content, "html.parser")


# 結果を格納するための辞書
data: dict = {}

# 学部を表す departmentName
for dept_name_div in soup.select(".departmentName"):
    # 学部名をテキストとして取得
    department_name = dept_name_div.get_text(strip=True).replace("＋", "").replace("―", "")
    if department_name not in data:
        data[department_name] = {}

    # departmentNameの兄弟要素として departmentSection があるので探索
    department_section = dept_name_div.find_next_sibling("div", class_="departmentSection")
    if not isinstance(department_section, Tag):
        continue

    # department_section 内には複数の openTitle があり、それぞれが「学科等」を表す
    for open_title_div in department_section.select(".openTitle"):
        category_name = open_title_div.get_text(strip=True).replace("＋", "").replace("―", "")
        if category_name not in data[department_name]:
            data[department_name][category_name] = []

        # openTitleの次の要素に syllabusses がある
        syllabusses_div = open_title_div.find_next_sibling("div", class_="syllabusses")
        if isinstance(syllabusses_div, Tag):
            # 講義タイトルを取得
            for syllabus_title_div in syllabusses_div.select(".syllabusTitle"):
                a_tag = syllabus_title_div.find("a")
                if isinstance(a_tag, Tag) and a_tag.text and a_tag.get("href"):
                    course_title = a_tag.get_text(strip=True)
                    # URLが相対パスの場合は結合
                    course_url = a_tag["href"]
                    if isinstance(course_url, str) and not course_url.startswith("http"):
                        course_url = base_url + course_url
                    data[department_name][category_name].append(
                        {"lecture_name": course_title, "lecture_no": get_lecture_no(course_url), "url": course_url}
                    )

# JSONとして出力
json_str = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)

# 必要ならファイル保存
with open("data/courses.json", "w", encoding="utf-8") as f:
    f.write(json_str)
