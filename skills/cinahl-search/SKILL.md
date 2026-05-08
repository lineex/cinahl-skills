---
name: cinahl-search
description: Search CINAHL on EBSCOhost by keyword or Boolean query and extract structured results. Use when the user wants to find nursing or allied-health papers in CINAHL.
argument-hint: "[search keywords or Boolean query]"
---

# CINAHL Basic Search

Search CINAHL on EBSCOhost through Chrome DevTools MCP.

## Determine EBSCO Context

Before searching, infer:

- `EBSCO_BASE`: current `origin + /c/{profile}` if the browser is already on `research.ebsco.com/c/{profile}` or a proxied equivalent.
- `CINAHL_DB`: current `db=` value, or `ccm` by default.

If no EBSCO page is open and no user-provided CINAHL link is available, ask for the user's institution CINAHL/EBSCOhost URL.

Common database codes: `ccm` CINAHL Complete, `rzh` CINAHL Plus with Full Text, `cul` CINAHL Ultimate, `cin20` CINAHL index, `c8h` CINAHL with Full Text.

## Steps

### Step 1: Navigate To Search Results

Build a new EBSCOhost search results URL:

```text
{EBSCO_BASE}/search/results?q={QUERY}&autocorrect=y&db={CINAHL_DB}&expanders=concept&limiters=None&searchMode=boolean&searchSegment=all-results
```

Use the raw user query from `$ARGUMENTS`, URL-encoded. Preserve Boolean syntax such as `AND`, `OR`, `NOT`, quotes, parentheses, `N3`, `W5`, truncation `*`, and field codes.

Always include:

```text
initScript: "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
```

### Step 2: Check Access

Use `evaluate_script` after navigation:

```javascript
() => {
  const text = document.body?.innerText || "";
  return {
    url: location.href,
    title: document.title,
    needsLogin: /login|shibboleth|sso|ezproxy|webvpn|institution|authenticate|sign in/i.test(location.href + "\n" + text),
    noAssignment: /user is not assigned|not authorized|access denied/i.test(text),
    challenge: /captcha|robot|security check|verify you are human/i.test(text)
  };
}
```

If login or assignment is required, tell the user: `页面被重定向，请在浏览器中完成登录或机构认证后告知我。`

If a challenge appears, try a fresh `take_snapshot` and click the visible verification checkbox if one exists. If not, tell the user: `请在浏览器中完成验证后告知我。`

### Step 3: Extract Results

Use `evaluate_script` with built-in waiting. Do not use `wait_for`.

```javascript
async () => {
  for (let i = 0; i < 24; i++) {
    if (document.querySelector('a[href*="/search/details/"], a[href*="AN="], a[href*="an="]')) break;
    await new Promise(r => setTimeout(r, 500));
  }

  const clean = s => (s || "").replace(/\s+/g, " ").trim();
  const uniq = arr => [...new Set(arr.filter(Boolean))];
  const pickTextAfter = (text, labels) => {
    for (const label of labels) {
      const re = new RegExp(label + "\\s*:?\\s*([^\\n]{2,220})", "i");
      const m = text.match(re);
      if (m) return clean(m[1]);
    }
    return "";
  };
  const nearestRecord = link => link.closest('article, li, [role="listitem"], [data-testid*="result"], .result, .record') || link.parentElement;

  const links = [...document.querySelectorAll('a[href*="/search/details/"], a[href*="direct=true"][href*="AN="], a[href*="direct=true"][href*="an="]')];
  const seen = new Set();
  const records = [];

  for (const link of links) {
    const href = link.href;
    const url = new URL(href, location.href);
    const key = url.href.split("#")[0];
    if (seen.has(key)) continue;
    seen.add(key);

    const box = nearestRecord(link);
    const text = clean(box?.innerText || link.innerText || "");
    const title = clean(link.innerText) || pickTextAfter(text, ["Title"]);
    if (!title || title.length < 5) continue;

    const params = url.searchParams;
    const db = params.get("db") || new URL(location.href).searchParams.get("db") || "";
    const an = params.get("AN") || params.get("an") || (text.match(/Accession Number[:\s]+([A-Z0-9-]+)/i)?.[1] || "");
    const detailId = url.pathname.match(/\/search\/details\/([^/?#]+)/)?.[1] || "";
    const doi = (text.match(/\b10\.\d{4,9}\/[-._;()/:A-Z0-9]+/i)?.[0] || "").replace(/[.,;)]$/, "");
    const pmid = text.match(/PMID[:\s]+(\d+)/i)?.[1] || "";
    const source = pickTextAfter(text, ["Source", "Journal", "Publication", "Published in"]) || "";
    const date = pickTextAfter(text, ["Publication Date", "Date", "Published"]) || (text.match(/\b(19|20)\d{2}\b/)?.[0] || "");
    const authors = uniq([...box.querySelectorAll('a[href*="AU="], button, [data-testid*="author"]')]
      .map(el => clean(el.innerText))
      .filter(v => v && v.length < 120 && !/full text|pdf|access|cite|save|share/i.test(v)));
    const fullText = /pdf full text|html full text|access now|full text/i.test(text);

    records.push({
      rank: records.length + 1,
      title,
      authors,
      source,
      date,
      doi,
      pmid,
      accessionNumber: an,
      detailId,
      db,
      fullText,
      url: key
    });
  }

  const pageText = clean(document.body?.innerText || "");
  const total = pageText.match(/([\d,]+)\s+results?/i)?.[0] || "";
  const currentUrl = location.href;
  return { records, totalResults: total, currentUrl };
}
```

If this returns zero records and the page text looks like the plain search form, use a fresh snapshot, fill the search textbox with `$ARGUMENTS`, click the Search button, then run the extraction script again. The new EBSCOhost UI may rewrite the URL to include `sqId` and `skipResultsFetch=true` after the first interactive search.

### Step 4: Present Results

Format as:

```text
Found {totalResults}

1. {title}
   Authors: {authors}
   Source: {source} | {date}
   DOI: {doi} | PMID: {pmid}
   DB/AN: {db}/{accessionNumber}
   Full text visible: yes/no
```

If no records are extracted, report the current URL and ask whether the page finished loading or requires institution login.

## Notes

- EBSCO query strings support Boolean operators, field tags, proximity operators, phrase quotes, and truncation. Preserve the user's syntax.
- CINAHL records are best tracked by `db + accessionNumber`; the new UI details id is useful but may be profile/session-specific.
