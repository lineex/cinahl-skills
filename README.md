# CINAHL Skills for Claude Code

English | 中文

Claude Code skills that let an agent operate CINAHL on EBSCOhost through Chrome DevTools MCP.

Search CINAHL, run advanced Boolean queries, parse result pages, open article records, browse publications, download available full text, export citations, and push records to Zotero.

## English

### Prerequisites

- Claude Code CLI installed
- Chrome browser with Chrome DevTools MCP enabled
- Institutional access to CINAHL through EBSCOhost, EZProxy, WebVPN, Shibboleth, SSO, or IP authentication
- Zotero desktop app, optional, for citation export
- Python 3, optional, for the Zotero helper script

### Skills

| Skill | Description | Invocation |
| --- | --- | --- |
| `cinahl-search` | Basic CINAHL keyword search with structured result extraction | `/cinahl-search pressure injury prevention` |
| `cinahl-advanced-search` | Fielded Boolean search using EBSCO/CINAHL field codes and common limiters | `/cinahl-advanced-search title:falls author:Smith year:2020-2026` |
| `cinahl-parse-results` | Re-parse the currently open CINAHL result list | Internal |
| `cinahl-navigate-pages` | Move through result pages, sort, and adjust result display | `/cinahl-navigate-pages next` |
| `cinahl-paper-detail` | Extract full article metadata, subject headings, abstract, DOI, PMID, and access links | `/cinahl-paper-detail AN=181230979 db=rzh` |
| `cinahl-journal-browse` | Search or open CINAHL publication pages and latest articles | `/cinahl-journal-browse Journal of Advanced Nursing` |
| `cinahl-download` | Download accessible PDF full text, or open HTML/full-text provider links | `/cinahl-download AN=181230979 db=rzh` |
| `cinahl-export` | Export RIS/BibTeX/plain text and optionally push records to Zotero | `/cinahl-export AN=181230979 db=rzh format: ris` |

### Agent

`cinahl-researcher` orchestrates all eight skills. It handles institutional login redirects, preserves the active EBSCO profile URL, supports both new EBSCOhost and classic direct links, and coordinates workflows such as search -> detail -> export -> download.

### Install Chrome DevTools MCP

```bash
claude mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest
```

Recommended Chrome launch settings:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "-y",
        "chrome-devtools-mcp@latest",
        "--ignoreDefaultChromeArg=--enable-automation",
        "--ignoreDefaultChromeArg=--disable-infobars",
        "--chromeArg=--disable-blink-features=AutomationControlled"
      ]
    }
  }
}
```

### Install The Skills

```bash
git clone <your-cinahl-skills-repo-url> cinahl-skills
cd cinahl-skills
cp -r skills/ agents/ .claude/
```

Or copy into an existing Claude Code project:

```bash
cp -r D:/AIcodex/cinahl-skills/skills your-project/.claude/skills/
cp -r D:/AIcodex/cinahl-skills/agents your-project/.claude/agents/
```

### EBSCO/CINAHL URL Strategy

The skills preserve whatever EBSCO URL the user's browser is already authenticated on:

- New EBSCOhost search results: `https://research.ebsco.com/c/{profile}/search/results?q={query}&autocorrect=y&db={db}&expanders=concept&limiters=None&searchMode=boolean&searchSegment=all-results`
- New EBSCOhost detail: `https://research.ebsco.com/c/{profile}/search/details/{recordId}?db={db}&limiters=None&q={query}&searchMode=boolean`
- Classic direct article link: `https://search.ebscohost.com/login.aspx?direct=true&db={db}&AN={accessionNumber}&site=ehost-live&scope=site`

Common CINAHL database codes:

| Code | Meaning |
| --- | --- |
| `ccm` | CINAHL Complete |
| `rzh` | CINAHL Plus with Full Text |
| `cul` | CINAHL Ultimate |
| `cin20` | CINAHL index |
| `c8h` | CINAHL with Full Text |

If no EBSCO page is open, start from the institution's EBSCO/CINAHL URL. Public profile IDs under `/c/{profile}` are institution-specific, so the agent should ask for the user's library link when it cannot infer one.

### Project Structure

```text
skills/
  cinahl-search/SKILL.md
  cinahl-advanced-search/SKILL.md
  cinahl-parse-results/SKILL.md
  cinahl-navigate-pages/SKILL.md
  cinahl-paper-detail/SKILL.md
  cinahl-journal-browse/SKILL.md
  cinahl-download/SKILL.md
  cinahl-export/
    SKILL.md
    scripts/
      push_to_zotero.py
agents/
  cinahl-researcher.md
```

## 中文

这是一套让 Claude Code 通过 Chrome DevTools MCP 操作 CINAHL/EBSCOhost 的技能集。整体结构模仿 `sd-skills`，但核心逻辑已替换为 EBSCOhost/CINAHL 的登录、检索、详情、全文下载和引用导出流程。

### 使用前提

- 已安装 Claude Code CLI
- 已配置 Chrome DevTools MCP
- Chrome 中可通过学校/医院/机构登录 CINAHL/EBSCOhost
- 可选：Zotero 桌面端，用于导出引用
- 可选：Python 3，用于 Zotero 推送脚本

### 安装

```bash
claude mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest
cp -r D:/AIcodex/cinahl-skills/skills your-project/.claude/skills/
cp -r D:/AIcodex/cinahl-skills/agents your-project/.claude/agents/
```

启动 Claude Code 后，可用 `/cinahl-search pressure injury prevention` 验证。第一次使用时建议先在 Chrome 中打开机构的 CINAHL/EBSCOhost 链接并完成登录。

### 登录逻辑

这些技能不会硬编码某个学校的登录地址。它们会优先读取当前浏览器中已经登录的 EBSCOhost 页面，并把该页面的 `origin + /c/{profile}` 保存为后续操作的基准地址。如果页面跳转到 SSO、Shibboleth、EZProxy、WebVPN 或登录页，agent 会暂停并提示用户在浏览器中完成认证，然后继续执行原任务。
