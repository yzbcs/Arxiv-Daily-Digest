# 📄 Arxiv Daily Digest

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
  <img src="https://img.shields.io/badge/LLM-MiniMax%20%7C%20Claude%20%7C%20OpenAI-orange" />
  <img src="https://img.shields.io/badge/Deploy-GitHub%20Actions-black?logo=github" />
</p>

<p align="center">
  <b>每天早上 8 点，自动把最新 arXiv 论文精选推送到你的邮箱。</b><br/>
  由 LLM 筛选 + 中文摘要 + 详细解读，fork 即用，无需服务器。
</p>

---

## 📸 效果预览

邮件以卡片形式展示每篇论文，包含一句话总结和可展开的详细解读：

- **一句话总结**：快速判断是否值得细读
- **详细解读**：点击展开，查看论文做了什么、核心创新点、主要结论
- **直达链接**：arXiv 原文 + PDF 一键跳转

---

## ✨ 核心功能

- 🔍 **关键词搜索**：支持多关键词，自动从 arXiv 检索 48 小时内最新论文
- 🤖 **LLM 智能筛选**：从 50 篇候选中精选最相关的 Top 10
- 🈶 **中文双层摘要**：一句话总结 + 100-150 字详细解读，阅读效率翻倍
- 📬 **HTML 邮件推送**：精美卡片排版，支持展开/收起详情
- 🔄 **去重机制**：记录已推送论文，48h 内不重复推送
- 🧩 **多 LLM 支持**：Claude / MiniMax / OpenAI / DeepSeek / 智谱 / Kimi / 通义，配置一行切换
- ⚙️ **零服务器部署**：完全基于 GitHub Actions，免费自动运行

---

## 🚀 快速开始

### 1. Fork 本仓库

点击右上角 **Fork**，将仓库复制到你的 GitHub 账号下。

### 2. 修改配置

编辑 `config.yml`，填写你关心的关键词：

```yaml
keywords:
  - agent
  - skill
  - your_keyword

categories:        # arxiv 分类，留空则全类别搜索
  - cs.AI
  - cs.LG

max_papers: 10     # 每日推送篇数
llm_provider: minimax  # LLM 提供商
```

### 3. 配置 GitHub Secrets

进入仓库 **Settings → Secrets and variables → Actions → New repository secret**，添加以下 4 个密钥：

| Secret 名称 | 说明 |
|------------|------|
| `LLM_API_KEY` | LLM 服务的 API Key |
| `EMAIL_USER` | 发件邮箱地址（163 / Gmail / QQ）|
| `EMAIL_PASS` | 发件邮箱授权码（非登录密码）|
| `EMAIL_TO` | 收件邮箱地址 |

### 4. 触发运行

进入 **Actions → Daily Paper Digest → Run workflow** 手动触发一次验证。

之后每天北京时间 **08:00** 自动推送。

---

## 🔧 支持的 LLM 提供商

在 `config.yml` 中修改 `llm_provider` 即可切换，所有提供商均使用同一套接口：

| provider | 服务商 | SDK |
|----------|--------|-----|
| `claude` | Anthropic Claude | Anthropic |
| `minimax` | MiniMax | Anthropic |
| `openai` | OpenAI GPT | OpenAI |
| `deepseek` | DeepSeek | OpenAI |
| `zhipu` | 智谱 GLM | OpenAI |
| `moonshot` | 月之暗面 Kimi | OpenAI |
| `qwen` | 阿里通义千问 | OpenAI |

> 新增提供商只需在 `llm/filter_and_summarize.py` 的 `PROVIDER_REGISTRY` 中注册一行。

---

## 📁 项目结构

```
arxiv-daily/
├── config.yml                  # ⭐ 用户配置文件（关键词、LLM、邮箱等）
├── main.py                     # 主入口
├── fetchers/
│   └── arxiv_fetcher.py        # arXiv API 搜索 + LaTeX 清洗 + 去重
├── llm/
│   └── filter_and_summarize.py # LLM 筛选 + 中文摘要 + 详细解读
├── render/
│   └── email_renderer.py       # Jinja2 HTML 渲染
├── templates/
│   └── email.html              # 邮件模板
├── sender/
│   └── smtp_sender.py          # SMTP 发送（163 / Gmail / QQ）
├── data/
│   └── sent_ids.json           # 已推送记录（去重缓存）
└── .github/workflows/
    └── daily.yml               # GitHub Actions 定时任务
```

---

## 💻 本地运行

```bash
git clone https://github.com/yzbcs/Arxiv-Daily-Digest.git
cd Arxiv-Daily-Digest
pip install -r requirements.txt

# 设置环境变量
export LLM_API_KEY="your_api_key"
export EMAIL_USER="xxx@163.com"
export EMAIL_PASS="your_smtp_password"
export EMAIL_TO="xxx@qq.com"

# 预览模式（不发邮件，生成 preview.html）
python3 main.py --dry-run

# 正式运行
python3 main.py
```

---

## 📮 邮箱授权码获取

**163 邮箱**：登录网页版 → 设置 → POP3/SMTP/IMAP → 开启 SMTP → 获取授权码

**Gmail**：开启两步验证 → 应用专用密码 → 生成

**QQ 邮箱**：设置 → 账户 → POP3/IMAP/SMTP → 开启 → 获取授权码

---

## 📄 License

MIT © [yzbcs](https://github.com/yzbcs)
