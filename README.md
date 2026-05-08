# CINAHL Skills for Claude Code

[English](#english) | [中文](#中文)

---

## English

Claude Code skills that let an agent operate CINAHL on EBSCOhost through Chrome DevTools MCP.

### Key Features

- **Smart Search**: Basic keyword search and advanced Boolean queries.
- **Result Parsing**: Extraction of metadata, subject headings, abstracts, DOI, and PMID.
- **Full-Text Access**: Automated PDF download and provider link navigation.
- **Workflow**: Search → Detail Extraction → Citation Export → Zotero → PDF Download.
- **Authentication**: Handles SSO, Shibboleth, EZProxy, and WebVPN redirects.

### Prerequisites

- Claude Code CLI
- Chrome Browser with [Chrome DevTools MCP](https://github.com/google/chrome-devtools-mcp)
- Institutional access to CINAHL/EBSCOhost
- (Optional) Zotero Desktop and Python 3

### Skills

| Skill | Description | Example |
| :--- | :--- | :--- |
| `cinahl-search` | Keyword search | `/cinahl-search "pressure injury"` |
| `cinahl-advanced-search` | Boolean search | `/cinahl-advanced-search title:falls` |
| `cinahl-paper-detail` | Extract metadata | `/cinahl-paper-detail AN=181230979` |
| `cinahl-export` | RIS/BibTeX/Zotero | `/cinahl-export AN=181230979` |
| `cinahl-download` | Download PDF | `/cinahl-download AN=181230979` |
| `cinahl-journal-browse` | Browse publications | `/cinahl-journal-browse "Nursing"` |

### Installation

```bash
# 1. Add MCP
claude mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest

# 2. Clone skills
git clone https://github.com/lineex/cinahl-skills.git
cd cinahl-skills

# 3. Copy to Claude Code
cp -r skills/ agents/ ~/.claude/
```

### EBSCO/CINAHL DB Codes

| Code | Database Name |
| :--- | :--- |
| `ccm` | CINAHL Complete |
| `rzh` | CINAHL Plus with Full Text |
| `cul` | CINAHL Ultimate |
| `c8h` | CINAHL with Full Text |

---

## 中文

Claude Code 技能集：通过 Chrome DevTools MCP 操作 CINAHL/EBSCOhost 数据库。

### 核心功能

- **智能检索**: 支持基础关键词及高级字段检索。
- **深度解析**: 自动提取元数据、主题词、摘要、DOI 和 PMID。
- **全文获取**: 自动化下载 PDF，处理第三方全文库跳转。
- **全流程**: 检索 → 详情 → 导出 → Zotero → PDF。
- **身份验证**: 适配 SSO, Shibboleth, EZProxy, WebVPN。

### 使用前提

- 已安装 Claude Code CLI
- 已配置 Chrome DevTools MCP
- 拥有 CINAHL/EBSCOhost 访问权限
- (可选) Zotero 桌面端及 Python 3

### 技能列表

| 技能名称 | 描述 | 调用示例 |
| :--- | :--- | :--- |
| `cinahl-search` | 关键词检索 | `/cinahl-search "护理干预"` |
| `cinahl-advanced-search` | 高级检索 | `/cinahl-advanced-search title:跌倒` |
| `cinahl-paper-detail` | 提取详情 | `/cinahl-paper-detail AN=181230979` |
| `cinahl-export` | 导出/推送 Zotero | `/cinahl-export AN=181230979` |
| `cinahl-download` | 下载 PDF | `/cinahl-download AN=181230979` |

### 安装步骤

```bash
# 1. 添加 MCP 服务
claude mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest

# 2. 克隆技能库
git clone https://github.com/lineex/cinahl-skills.git
cd cinahl-skills

# 3. 部署到配置目录
cp -r skills/ agents/ ~/.claude/
```

---

### Project Structure

```text
skills/
  cinahl-search/              # Keyword searching
  cinahl-advanced-search/     # Boolean logic
  cinahl-parse-results/       # Result extraction
  cinahl-navigate-pages/      # Pagination
  cinahl-paper-detail/        # Record extraction
  cinahl-journal-browse/      # Publication lookup
  cinahl-download/            # PDF acquisition
  cinahl-export/              # Citation export
agents/
  cinahl-researcher.md        # Main agent
```

