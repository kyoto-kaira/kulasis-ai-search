from typing import Optional
from urllib.parse import parse_qs, urlparse


def get_lecture_no(url: str) -> Optional[str]:
    """
    URLから講義番号を取得する

    Parameters
    ----------
    url : str
        シラバスのURL

    Returns
    -------
    Optional[str]
        lectureNoの値, 存在しない場合はNone
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    lecture_no = query_params.get("lectureNo", [None])[0]
    return lecture_no
