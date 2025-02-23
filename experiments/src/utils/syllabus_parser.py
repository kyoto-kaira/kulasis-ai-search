from typing import Dict, Optional

from bs4 import BeautifulSoup
from bs4.element import Tag


class SyllabusParser:
    def __init__(self, html: str) -> None:
        self.soup = BeautifulSoup(html, "html.parser")

    def _get_text_after_subheading(self, heading_text: str) -> Optional[str]:
        """
        '(授業の概要・目的)'などのサブヘッダ文字列にマッチするdiv.lesson_plan_subheading要素を探し、
        次の兄弟ノードまたは親要素内のテキストを取得するためのユーティリティメソッド。
        """
        # lesson_plan_subheadingのdivを全て取得
        subheadings = self.soup.find_all("div", class_="lesson_plan_subheading")
        for sub in subheadings:
            if heading_text in sub.get_text(strip=True):
                # subheadingの親要素には次に続くテキストが格納されているケースが多い
                # subheadingの次のdivもしくは同列の内容を取得する
                # 基本的には次のsiblingや同じセル内の次のテキストノードをたどる
                parent_td = sub.find_parent("td", class_="lesson_plan_sell")
                if not parent_td or not sub.parent:
                    # 見つからない場合は次の兄弟要素など別の方法で探す必要あり
                    continue
                # subheading自体の次にあるテキストを取得
                # subheadingの親要素内でsubheading後に続くテキスト（<div>など）を抽出
                texts = []
                for elem in sub.parent.find_all(string=True, recursive=False):
                    # sub itselfのテキストは除外
                    if isinstance(elem, str) and sub.get_text(strip=True) not in elem.strip():
                        if elem.strip() and isinstance(elem, str):
                            texts.append(elem.strip())

                # もし上記で取れなければ子要素(divなど)も走査
                for child in sub.parent.find_all():
                    if child == sub:
                        continue
                    # subheading以降のテキストノードを収集
                    # ここはHTML構造に合わせて微調整
                    if child.get_text(strip=True):
                        if sub.get_text(strip=True) != child.get_text(strip=True):
                            texts.append(child.get_text(strip=True))
                # textsの中身を改行でつなげる
                return "\n".join(texts).strip()
        return None

    def parse(self) -> Dict[str, Optional[str]]:
        result: Dict[str, Optional[str]] = {}

        # 科目ナンバリング:
        # テキスト中で「(科目ナンバリング)」の直後の行にある。
        numbering_td = self.soup.find(
            "span", class_="lesson_plan_subheading", string=lambda x: x and "(科目ナンバリング)" in x
        )
        if numbering_td:
            # numbering_tdの親要素tableから、対応する次のtdを取得
            numbering_parent = numbering_td.find_parent("table")
            if isinstance(numbering_parent, Tag):
                # 実際の科目ナンバリングテキストは (科目ナンバリング) の行のすぐ下にある
                # <td nowrap>U-ECON00 10102 LJ43</td> のような箇所
                text_nodes = numbering_parent.find_all("td")
                # text_nodes[1] 辺りに格納されていることが多いが、固定的ではないのでキーワード検索する
                for td in text_nodes:
                    if "U-ECON00" in td.get_text(strip=True):
                        result["科目ナンバリング"] = td.get_text(strip=True)
                        break

        # 英訳: 「(英 訳)」の行を探す
        eng_td = self.soup.find("span", class_="lesson_plan_subheading", string=lambda x: x and "(英 訳)" in x)
        if eng_td:
            eng_parent = eng_td.find_parent("table")
            if isinstance(eng_parent, Tag):
                # 英訳は(英 訳)行の次のtdにあると想定
                # tdを全取得し、(英 訳)があったらその次のtdを取る
                tds = eng_parent.find_all("td")
                # tdsに(英 訳)が含まれる位置を特定
                for i, td in enumerate(tds):
                    if "英 訳" in td.get_text():
                        # 次のtdが英訳
                        if i + 1 < len(tds):
                            result["英訳"] = tds[i + 1].get_text(strip=True)
                        break

        # 所属部局, 職名, 氏名:
        # 「(所属部局)」「(職 名)」「(氏 名)」はtable内の行を見る
        teacher_info_table = self.soup.find("td", class_="lesson_plan_sell", string=lambda x: x and "(所属部局)" in x)
        if teacher_info_table:
            # 対象のtdは"所属部局"のテキストを含むノードとは限らないため親方向を再探索
            teacher_info_table = teacher_info_table.find_parent("table")
        else:
            # 直接発見できない場合はサブヘッダではなく連続的な行を探す
            # 所属部局, 職名, 氏名の行は "(科目名)" などがあるテーブルの隣のtd内にある。
            # もうひとつ方法としては、"(所属部局)"のdivを探す
            subheading = self.soup.find("span", class_="lesson_plan_subheading", string="(所属部局)")
            if subheading:
                teacher_info_table = subheading.find_parent("table")

        if isinstance(teacher_info_table, Tag):
            # このテーブル内には (所属部局), (職 名), (氏 名) のヘッダと値が並んでいる
            # 次の行に実データあり
            rows = teacher_info_table.find_all("tr")

            # ヘッダ行を見つけ、その下の行を値として取得する
            for i, row in enumerate(rows):
                if "(所属部局)" in row.get_text():
                    # 次の行にデータがあるはず
                    next_row = rows[i + 1]
                    if i + 1 < len(rows) and isinstance(next_row, Tag):
                        data_row = next_row.find_all("td")
                        # data_rowは[所属部局, 職名, 氏名]の順
                        if len(data_row) >= 3:
                            result["所属部局"] = data_row[0].get_text(strip=True)
                            result["職名"] = data_row[1].get_text(strip=True)
                            result["氏名"] = data_row[2].get_text(strip=True)
                    break

        # 配当学年, 単位数, 開講年度・開講期:
        # (配当学年), (単位数), (開講年度・開講期)は同じ行または隣接行にある
        # "(配当学年)"が記載されている行を探す
        year_td = self.soup.find("span", class_="lesson_plan_subheading", string=lambda x: x and "(配当学年)" in x)
        if year_td:
            parent_table = year_td.find_parent("table")
            if isinstance(parent_table, Tag):
                tds = parent_table.find_all("td")
                # 順番的に (配当学年) -> 1,2回生 -> (単位数) -> 2単位 -> (開講年度・開講期) -> 2024・前期
                # を想定
                texts = [td.get_text(strip=True) for td in tds]
                # texts例: ["(配当学年)", "1,2回生", "(単位数)", "2単位", "(開講年度・開講期)", "2024・前期"]
                if "(配当学年)" in texts:
                    idx = texts.index("(配当学年)")
                    if idx + 1 < len(texts):
                        result["配当学年"] = texts[idx + 1]
                if "(単位数)" in texts:
                    idx = texts.index("(単位数)")
                    if idx + 1 < len(texts):
                        result["単位数"] = texts[idx + 1]
                if "(開講年度・開講期)" in texts:
                    idx = texts.index("(開講年度・開講期)")
                    if idx + 1 < len(texts):
                        result["開講年度・開講期"] = texts[idx + 1]

        # 曜時限, 授業形態:
        # "(曜時限)" と "(授業形態)" のあるテーブルを探す
        day_time_td = self.soup.find("span", class_="lesson_plan_subheading", string=lambda x: x and "(曜時限)" in x)
        if day_time_td:
            parent_table = day_time_td.find_parent("table")
            if isinstance(parent_table, Tag):
                tds = parent_table.find_all("td")
                texts = [td.get_text(strip=True) for td in tds]
                # 想定: ["(曜時限)", "水2", "(授業形態)", "講義"]
                if "(曜時限)" in texts:
                    idx = texts.index("(曜時限)")
                    if idx + 1 < len(texts):
                        result["曜時限"] = texts[idx + 1]
                if "(授業形態)" in texts:
                    idx = texts.index("(授業形態)")
                    if idx + 1 < len(texts):
                        result["授業形態"] = texts[idx + 1]

        # 使用言語
        lang_td = self.soup.find("span", class_="lesson_plan_subheading", string=lambda x: x and "(使用言語)" in x)
        if lang_td:
            parent_table = lang_td.find_parent("table")
            if isinstance(parent_table, Tag):
                tds = parent_table.find_all("td")
                # 想定: ["(使用言語)", "日本語"]
                for i, td in enumerate(tds):
                    if "(使用言語)" in td.get_text():
                        if i + 1 < len(tds):
                            result["使用言語"] = tds[i + 1].get_text(strip=True)
                        break

        # 授業の概要・目的
        result["授業の概要・目的"] = self._get_text_after_subheading("(授業の概要・目的)")

        # 到達目標
        result["到達目標"] = self._get_text_after_subheading("(到達目標)")

        # 授業計画と内容
        result["授業計画と内容"] = self._get_text_after_subheading("(授業計画と内容)")

        # 履修要件
        result["履修要件"] = self._get_text_after_subheading("(履修要件)")

        # 成績評価の方法・観点
        result["成績評価の方法・観点"] = self._get_text_after_subheading("(成績評価の方法・観点)")

        # 教科書
        # (教科書) はdiv.lesson_plan_subheadingもしくはspan.lesson_plan_subheadingで探す
        textbook_sub = self.soup.find("span", class_="lesson_plan_subheading", string=lambda x: x and "(教科書)" in x)
        if textbook_sub:
            parent_td = textbook_sub.find_parent("td", class_="lesson_plan_sell")
            if parent_td:
                # subheading以降のテキスト収集
                result["教科書"] = "\n".join(
                    [t.strip() for t in parent_td.get_text("\n").split("\n") if t.strip() and "(教科書)" not in t]
                ).strip()

        # 参考書等
        ref_sub = self.soup.find("span", class_="lesson_plan_subheading", string=lambda x: x and "(参考書等)" in x)
        if ref_sub:
            parent_td = ref_sub.find_parent("td", class_="lesson_plan_sell")
            if parent_td:
                result["参考書等"] = "\n".join(
                    [t.strip() for t in parent_td.get_text("\n").split("\n") if t.strip() and "(参考書等)" not in t]
                ).strip()

        # 授業外学修（予習・復習）等
        result["授業外学修（予習・復習）等"] = self._get_text_after_subheading("(授業外学修（予習・復習）等)")

        return result

    def get_text(self) -> str:
        """
        抽出した情報をもとに、シラバスのテキストを生成する
        """
        data = self.parse()
        text = ""
        for k, v in data.items():
            text += f"{k}: {v}\n"
        return text


if __name__ == "__main__":
    with open("data/htmls/全学共通科目/53543.html", "r", encoding="utf-8") as f:
        html = f.read()
    parser = SyllabusParser(html)
    data = parser.parse()
    for k, v in data.items():
        print(k, ":", v)
