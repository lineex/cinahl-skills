# CINAHL Skills for Claude Code

<p align="center">
  <a href="#english">English</a> | <a href="#chinese">中文</a>
</p>

---

<a name="english"></a>
## English

Claude Code skills that let an agent operate **CINAHL (Cumulative Index to Nursing and Allied Health Literature)** on EBSCOhost through Chrome DevTools MCP.

### Key Features

*   **Smart Search**: Basic keyword search and advanced Boolean queries using EBSCO/CINAHL field codes.
*   **Result Parsing**: Deep extraction of article metadata, subject headings, abstracts, and identifiers (DOI, PMID).
*   **Full-Text Access**: Automated download of PDF full text and navigation of full-text provider links.
*   **Workflow Integration**: Search → Detail Extraction → Citation Export (RIS/BibTeX) → Zotero Integration → PDF Download.
*   **Adaptive Authentication**: Handles institutional redirects (SSO, Shibboleth, EZProxy, WebVPN) by preserving active session context.

### Prerequisites

*   **Claude Code CLI** installed.
*   **Chrome Browser** with [Chrome DevTools MCP](https://github.com/google/chrome-devtools-mcp) enabled.
*   **Institutional Access** to CINAHL via EBSCOhost.
*   *(Optional)* **Zotero Desktop** for citation management.
*   *(Optional)* **Python 3** for the Zotero helper script.

### Available Skills

| Skill | Description | Example Invocation |
| :--- | :--- | :--- |
| `cinahl-search` | Keyword search with structured results. | `/cinahl-search "pressure injury prevention"` |
| `cinahl-advanced-search` | Fielded Boolean search with limiters. | `/cinahl-advanced-search title:falls author:Smith year:2020-2026` |
| `cinahl-paper-detail` | Extract full metadata and access links. | `/cinahl-paper-detail AN=181230979 db=rzh` |
| `cinahl-export` | Export RIS/BibTeX or push to Zotero. | `/cinahl-export AN=181230979 db=rzh format:ris` |
| `cinahl-download` | Download PDF or open provider links. | `/cinahl-download AN=181230979 db=rzh` |
| `cinahl-journal-browse` | Browse publications and latest issues. | `/cinahl-journal-browse "Journal of Advanced Nursing"` |
| `cinahl-navigate-pages` | Pagination, sorting, and display options. | `/cinahl-navigate-pages next` |
| `cinahl-parse-results` | Re-parse current result list. | *Internal Use* |

### Installation

1. **Add Chrome DevTools MCP**:
   ```bash
   claude mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest
   ```

2. **Clone and Install Skills**:
   ```bash
   git clone https://github.com/lineex/cinahl-skills.git
   cd cinahl-skills
   # Copy to your Claude Code configuration directory
   cp -r skills/ agents/ ~/.claude/
   ```

### EBSCO/CINAHL URL Strategy

The skills are designed to be environment-agnostic. They preserve the `{profile}` ID and `{db}` codes from your active session.

| CINAHL DB Code | Database Name |
| :--- | :--- |
| `ccm` | CINAHL Complete |
| `rzh` | CINAHL Plus with Full Text |
| `cul` | CINAHL Ultimate |
| `c8h` | CINAHL with Full Text |

---

<a name="chinese"></a>
## 中文 (Chinese)

这是一套专为 Claude Code 设计的技能集，通过 Chrome DevTools MCP 赋予 Agent 直接操作 **CINAHL (护理学及相关健康治疗全文数据库)** 的能力。

### 核心功能

*   **智能检索**: 支持基础关键词搜索及使用 EBSCO 字段代码的布尔逻辑高级检索。
*   **深度解析**: 自动提取文章元数据、核心主题词 (Subject Headings)、摘要及 DOI/PMID。
*   **全文获取**: 自动化下载 PDF 全文，支持处理第三方全文库跳转。
*   **全流程自动化**: 检索 → 详情提取 → 引用导出 (RIS/BibTeX) → 推送 Zotero → 下载 PDF。
*   **身份验证适配**: 完美适配机构认证 (SSO, Shibboleth, EZProxy, WebVPN)，自动保存活动会话上下文。

### 使用前提

*   已安装 **Claude Code CLI**。
*   已配置 **Chrome DevTools MCP**。
*   拥有机构提供的 **CINAHL/EBSCOhost 访问权限**。
*   （可选）**Zotero 桌面端**，用于文献管理。
*   （可选）**Python 3**，用于执行 Zotero 推送脚本。

### 技能列表

| 技能名称 | 描述 | 调用示例 |
| :--- | :--- | :--- |
| `cinahl-search` | 基础关键词检索及结果提取 | `/cinahl-search "护理干预 压疮"` |
| `cinahl-advanced-search` | 字段布尔检索及筛选条件 | `/cinahl-advanced-search title:跌倒 author:张三 year:2022-2025` |
| `cinahl-paper-detail` | 提取全文元数据及访问链接 | `/cinahl-paper-detail AN=181230979 db=rzh` |
| `cinahl-export` | 导出引用或推送到 Zotero | `/cinahl-export AN=181230979 db=rzh format:ris` |
| `cinahl-download` | 下载 PDF 或打开全文链接 | `/cinahl-download AN=181230979 db=rzh` |

### 安装步骤

1. **添加 Chrome 调试服务**:
   ```bash
   claude mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest
   ```

2. **克隆并部署技能**:
   ```bash
   git clone https://github.com/lineex/cinahl-skills.git
   cd cinahl-skills
   # 复制到您的 Claude Code 配置目录
   cp -r skills/ agents/ ~/.claude/
   ```

### 登录与 URL 策略

这些技能不会硬编码特定的机构登录地址。它们会优先读取当前浏览器中已经登录的页面，并自动识别 `profile` ID。如果检测到需要重新认证（如跳转至登录页），Agent 会提示用户在浏览器中手动完成认证后继续。

---

### Project Structure

```text
skills/
  cinahl-search/SKILL.md            # Keyword searching
  cinahl-advanced-search/SKILL.md   # Advanced Boolean logic
  cinahl-parse-results/SKILL.md     # Result extraction
  cinahl-navigate-pages/SKILL.md    # Pagination & sorting
  cinahl-paper-detail/SKILL.md      # Full record extraction
  cinahl-journal-browse/SKILL.md    # Publication lookup
  cinahl-download/SKILL.md          # PDF acquisition
  cinahl-export/                    # RIS/BibTeX export
    SKILL.md
    scripts/
      push_to_zotero.py
agents/
  cinahl-researcher.md              # Main orchestrator agent
```

