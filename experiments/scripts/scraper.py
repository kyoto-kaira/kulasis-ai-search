import asyncio
import json
import os
import time
from collections import defaultdict

import aiofiles
import aiohttp
import requests
from bs4 import BeautifulSoup
from src.constants import DEPARTMENTS

from .common import get_lecture_no


def scrape_lecture_urls() -> None:
    """
    京都大学のシラバスページから講義のURLをスクレイピングして、JSONファイルに保存する
    """
    BASE_URL = "https://www.k.kyoto-u.ac.jp/external/open_syllabus/"
    urls_dict = defaultdict(list)
    response = requests.get(BASE_URL + "all")
    response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
    soup = BeautifulSoup(response.content, "html.parser")

    department_divs = soup.find_all("div", class_="departmentName")

    for dept in department_divs:
        department_name = dept.get_text(strip=True)
        # 部門名の最後の文字を除去して比較
        if department_name[:-1] in DEPARTMENTS:
            parent_div = dept.find_parent()

            if not parent_div:
                continue

            department_section = parent_div.find("div", class_="departmentSection")
            if not department_section:
                continue

            syllabus_titles = department_section.find_all("div", class_="syllabusTitle")

            for syllabus in syllabus_titles:
                a_tag = syllabus.find("a")
                if a_tag and "href" in a_tag.attrs:
                    href = a_tag["href"]
                    lecture_name = a_tag.get_text(strip=True)
                    # lecture_noを取得する際に、完全なURLを使用
                    full_url = BASE_URL + href
                    lecture_no = get_lecture_no(full_url)
                    urls_dict[department_name[:-1]].append(
                        {"lecture_name": lecture_name, "url": full_url, "lecture_no": lecture_no}
                    )

    # ディレクトリが存在しない場合は作成
    os.makedirs("data", exist_ok=True)

    with open("data/lecture_urls.json", mode="w", encoding="utf-8") as f:
        json.dump(urls_dict, f, ensure_ascii=False, indent=4)


URL_LIST_FILE = "data/lecture_urls.json"
OUTPUT_DIR = "data/htmls"
FAILED_URLS_FILE = "data/failed_urls.txt"
os.makedirs(OUTPUT_DIR, exist_ok=True)


async def fetch_html(session: aiohttp.ClientSession, url: str, file_path: str, semaphore: asyncio.Semaphore) -> None:
    async with semaphore:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                content = await response.read()
                html = content.decode("CP932")
                async with aiofiles.open(file_path, "w") as f:
                    await f.write(html)
                print(f"Downloaded: {url} -> {file_path}")
                time.sleep(1)
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            with open(FAILED_URLS_FILE, "a") as f:
                f.write(f"{url}\n")


async def main() -> None:
    # JSONファイルからURLリストを読み込む
    async with aiofiles.open(URL_LIST_FILE, "r", encoding="utf-8") as f:
        content = await f.read()
        urls_dict = json.loads(content)

    # セマフォを使用して同時接続数を制限（例：10）
    semaphore = asyncio.Semaphore(10)

    async with aiohttp.ClientSession() as session:
        tasks = []
        for department, lectures in urls_dict.items():
            # 各学部ごとにサブディレクトリを作成
            department_dir = os.path.join(OUTPUT_DIR, department)
            os.makedirs(department_dir, exist_ok=True)

            for lecture in lectures:
                url = lecture["url"]
                lecture_no = lecture["lecture_no"]
                if lecture_no:
                    file_name = f"{lecture_no}.html"
                else:
                    # lecture_noがない場合は、講義名からファイル名を生成
                    sanitized_name = "".join(c if c.isalnum() else "_" for c in lecture["lecture_name"])
                    file_name = f"{sanitized_name}.html"

                if os.path.exists(os.path.join(department_dir, file_name)):
                    print(f"Skipping {url} -> {file_name}")
                    continue

                if os.path.exists(FAILED_URLS_FILE):
                    os.remove(FAILED_URLS_FILE)

                file_path = os.path.join(department_dir, file_name)
                task = asyncio.create_task(fetch_html(session, url, file_path, semaphore))
                tasks.append(task)

        # 全てのタスクを並列に実行
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    scrape_lecture_urls()
    asyncio.run(main())
