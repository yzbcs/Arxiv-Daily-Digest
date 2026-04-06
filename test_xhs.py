"""测试小红书抓取 + LLM 筛选，不跑 arXiv。"""

import os
import sys
import yaml

from fetchers.xhs_fetcher import fetch_xhs_notes
from llm.filter_and_summarize_xhs import filter_and_summarize_xhs

cfg = yaml.safe_load(open("config.yml", encoding="utf-8"))
keywords = cfg.get("xhs_keywords") or cfg.get("keywords", [])
pool = cfg.get("xhs_candidate_pool", 30)
max_papers = cfg.get("max_papers", 10)
min_score = cfg.get("min_score", 6)
llm_provider = cfg.get("llm_provider", "minimax")

cookie = os.environ.get("XHS_COOKIE", "").strip()
api_key = os.environ.get("LLM_API_KEY", "").strip()
if not cookie:
    print("[ERROR] 请先 export XHS_COOKIE=...", file=sys.stderr)
    sys.exit(1)

print(f"[1/2] 搜索小红书，关键词: {keywords}")
candidates = fetch_xhs_notes(keywords, pool, cookie)
print(f"      候选笔记: {len(candidates)} 条")
for i, n in enumerate(candidates[:5]):
    print(f"      {i+1}. {n['title'][:40]}  ❤️{n['liked_count']}")

if not candidates:
    print("没有候选笔记，结束")
    sys.exit(0)

if not api_key or api_key in ("dummy", "test"):
    print("[SKIP] LLM_API_KEY 未设置，跳过筛选")
    sys.exit(0)

print(f"[2/2] LLM 筛选（{llm_provider}）")
notes = filter_and_summarize_xhs(candidates, keywords, max_papers, llm_provider, api_key, min_score)
print(f"      精选: {len(notes)} 条")
for i, n in enumerate(notes):
    print(f"      {i+1}. [score={n.get('score',0)}] {n['title'][:40]}")
    print(f"         {n.get('summary_zh', '')}")
