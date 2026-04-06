# 小红书集成高频问题与解决方案

> 本文档记录在本地和 GitHub Actions 中运行小红书功能时遇到的问题及修复方案。

---

## 1. ModuleNotFoundError: No module named 'execjs'

**错误信息**:
```
ModuleNotFoundError: No module named 'execjs'
```

**原因**: Python 的 execjs 库在 PyPI 上的包名是 `PyExecJS`，而非 `execjs`。

**解决**: 安装正确的包名：
```bash
pip install PyExecJS
```

---

## 2. Node.js v22+ stdin TypeScript parser 导致 SyntaxError

**错误信息**:
```
SyntaxError: Unexpected token ':'
SyntaxError: Unexpected token '<'
```

**原因**: Node.js v22+ 将 stdin 输入当作 TypeScript 解析，而 Spider_XHS 提供的 JS 签名文件是 webpack 打包的 bundle（包含 TypeScript 语法如 `interface`），导致解析失败。

**解决**: 强制 execjs 使用临时文件模式（.js 文件）而非 stdin：
```python
_node_rt = execjs.get()
_node_rt._tempfile = True
```

---

## 3. crypto-js not found from /tmp/

**错误信息**:
```
Error: Cannot find module 'crypto-js'
```

**原因**: execjs 的临时文件模式将 JS 代码写到系统 `/tmp/` 目录执行，Node.js 在该目录下无法找到项目根目录 `node_modules` 中的 `crypto-js` 模块。

**解决**: 设置 `NODE_PATH` 环境变量指向项目 node_modules：
```python
_project_root = Path(__file__).parent.parent
os.environ["NODE_PATH"] = str(_project_root / "node_modules")
```

---

## 4. xhs_xray.js 语法错误

**错误信息**:
```
SyntaxError: Cannot use import statement
```

**原因**: `xhs_xray.js` 是 webpack 打包的 bundle，在 Node.js v25 的 CJS 加载器下存在语法兼容问题。

**解决**: 该文件生成的 `x-xray-traceid`  header 为非必需字段，直接返回空字符串绕过：
```python
def generate_xray_traceid():
    return ""
```

---

## 5. 搜索结果前3条返回"笔记不存在"

**错误信息**:
```
[XHS] 获取笔记详情失败 abc123: 笔记不存在
```

**原因**: 搜索结果的前几条通常是**推广/广告笔记**（`model_type` 为 `promote` 或其他值），它们的详情接口不返回真实内容。

**解决**: 在搜索结果循环中过滤非正常笔记：
```python
if note.get("model_type") not in ("note", None):
    continue
```

---

## 6. 笔记 ID 带 #timestamp 后缀

**错误信息**:
```
笔记不存在
```

**原因**: 小红书搜索 API 返回的笔记 ID 带有时间戳后缀，格式如 `abc123#1775479505847`，直接拼接 URL 会导致请求失败。

**解决**: 拼接 URL 前去除后缀：
```python
note_id = note_id.split("#")[0]
```

---

## 7. id / xsec_token 位置错误

**错误信息**:
```
笔记不存在
```

**原因**: 早期代码从 `note_card` 中读取 `id` 和 `xsec_token`，但这两个字段实际位于搜索结果 JSON 的**顶层**，而非 `note_card` 内。

**解决**: 从搜索结果顶层读取：
```python
note_id = note.get("id", "")       # 顶层，不是 note_card 内部
xsec_token = note.get("xsec_token", "")
display_title = note.get("note_card", {}).get("display_title", "")  # note_card 里是展示信息
```

---

## 8. GitHub Actions 中 XHS_COOKIE 配置

**问题**: 如何在 GitHub Actions 中配置小红书 Cookie？

**解决**:
1. 在本地浏览器登录小红书网页版（chrome://settings/cookies）
2. 打开 F12 → Application → Cookies → www.xiaohongshu.com，复制 `a1` 等 Cookie 值
3. 拼接成字符串格式：`a1=xxx; webId=xxx; ...`
4. 进入 GitHub 仓库 → **Settings → Secrets and variables → Actions → New repository secret**
5. Name 填 `XHS_COOKIE`，Value 粘贴完整 Cookie 字符串

**注意**: Cookie 有有效期（约30天），失效后需重新更新 GitHub Secret。

---

## 问题排查流程

1. **先跑 test_xhs.py** 单独验证小红书模块，不走 arXiv：
   ```bash
   export XHS_COOKIE="your_cookie"
   python3 test_xhs.py
   ```

2. **确认 Node.js 版本**（推荐 v18，v25 有兼容问题）：
   ```bash
   node --version
   ```

3. **确认 npm install 已执行**，node_modules 中有 crypto-js：
   ```bash
   ls node_modules/crypto-js
   ```
