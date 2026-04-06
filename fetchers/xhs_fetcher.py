"""
小红书笔记搜索。

对每个关键词调用搜索接口获取候选笔记，正文通过 get_note_info() 二次请求获取。
搜索结果仅保留一天内发布（note_time=1），按点赞数降序返回。
"""

import time
from fetchers.xhs_pc_apis import XHS_Apis


def fetch_xhs_notes(
    keywords: list[str],
    candidate_pool: int,
    cookies_str: str,
    proxies: dict | None = None,
) -> list[dict]:
    """
    搜索小红书笔记并返回候选列表。

    Args:
        keywords: 搜索关键词列表（与 config.yml 的 xhs_keywords 对应）
        candidate_pool: 最大候选数量
        cookies_str: 从浏览器 F12 复制的 Cookie 字符串
        proxies: 可选代理，格式 {"https": "http://127.0.0.1:7890"}

    Returns:
        list of dict，每项含 id / title / content / liked_count /
        url / xsec_token / matched_keywords
    """
    if not keywords or not cookies_str.strip():
        return []

    apis = XHS_Apis()
    per_kw = max(1, candidate_pool // len(keywords))

    seen_ids: set[str] = set()
    raw_notes: list[dict] = []

    for kw in keywords:
        success, msg, notes = apis.search_some_note(
            query=kw,
            require_num=per_kw,
            cookies_str=cookies_str,
            sort_type_choice=0,  # 综合排序
            note_time=1,         # 仅一天内发布的笔记
            proxies=proxies,
        )
        if not success:
            print(f"      [XHS] 搜索关键词 '{kw}' 失败: {msg}")
            continue

        for note in (notes or []):
            # 跳过广告/推广笔记，它们的详情接口会返回"笔记不存在"
            if note.get("model_type") not in ("note", None):
                continue
            # id 和 xsec_token 在搜索结果的顶层，note_card 里是标题/封面等展示信息
            note_id = note.get("id", "")
            # 小红书搜索 API 返回的 id 可能带 #timestamp 后缀（如 abc123#1775479505847），需去除
            note_id = note_id.split("#")[0]
            if not note_id or note_id in seen_ids:
                continue
            seen_ids.add(note_id)
            xsec_token = note.get("xsec_token", "")
            note_card = note.get("note_card", {})
            raw_notes.append({
                "_raw": note,
                "id": note_id,
                "xsec_token": xsec_token,
                "display_title": note_card.get("display_title", ""),
                "matched_keywords": [kw],
            })

    # 合并同一笔记命中的多个关键词
    merged: dict[str, dict] = {}
    for item in raw_notes:
        nid = item["id"]
        if nid in merged:
            merged[nid]["matched_keywords"] = list(set(
                merged[nid]["matched_keywords"] + item["matched_keywords"]
            ))
        else:
            merged[nid] = item

    # 二次请求：获取正文
    results = []
    for item in list(merged.values())[:candidate_pool]:
        note_id = item["id"]
        xsec_token = item["xsec_token"]
        url = f"https://www.xiaohongshu.com/explore/{note_id}?xsec_token={xsec_token}&xsec_source=pc_search"

        success, msg, note_info = apis.get_note_info(url, cookies_str, proxies)
        time.sleep(0.5)  # 避免请求过快

        if not success or note_info is None:
            print(f"      [XHS] 获取笔记详情失败 {note_id}: {msg}")
            continue

        try:
            card = note_info["data"]["items"][0]["note_card"]
            title = card.get("title") or card.get("display_title") or ""
            content = card.get("desc", "").replace("\n", " ").strip()
            interact = card.get("interact_info", {})
            liked_count = _parse_count(interact.get("liked_count", "0"))

            results.append({
                "id": note_id,
                "title": title,
                "content": content,
                "liked_count": liked_count,
                "url": url,
                "matched_keywords": item["matched_keywords"],
            })
        except (KeyError, IndexError, TypeError) as e:
            print(f"      [XHS] 解析笔记 {note_id} 失败: {e}")
            continue

    # 按点赞数降序
    results.sort(key=lambda x: x["liked_count"], reverse=True)
    return results[:candidate_pool]


def _parse_count(raw: str) -> int:
    """将小红书的点赞数字符串（如 '1.2万'）转为整数。"""
    if not raw:
        return 0
    raw = str(raw).strip()
    if "万" in raw:
        try:
            return int(float(raw.replace("万", "")) * 10000)
        except ValueError:
            return 0
    try:
        return int(raw)
    except ValueError:
        return 0
