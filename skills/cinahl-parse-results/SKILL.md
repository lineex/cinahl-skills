---
name: cinahl-parse-results
description: Re-parse the currently open CINAHL/EBSCOhost search result page. Internal skill used by other CINAHL skills.
user-invokable: false
---

# Parse Current CINAHL Results Page

Extract structured records from an already-open CINAHL/EBSCOhost result list without navigation.

## When To Use

- The user manually navigated to an EBSCOhost result list.
- Another skill changed sort, filters, or page number.
- You need to re-read the current page after login.

## Steps

Use a single `evaluate_script` call:

```javascript
() => {
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
  const urlDb = (() => {
    try { return new URL(location.href).searchParams.get("db") || ""; }
    catch { return ""; }
  })();

  if (!/ebsco|search/.test(location.href)) {
    return { error: "Not on an EBSCOhost search page.", currentUrl: location.href };
  }

  const links = [...document.querySelectorAll('a[href*="/search/details/"], a[href*="direct=true"][href*="AN="], a[href*="direct=true"][href*="an="]')];
  const seen = new Set();
  const records = [];

  for (const link of links) {
    const url = new URL(link.href, location.href);
    const key = url.href.split("#")[0];
    if (seen.has(key)) continue;
    seen.add(key);

    const box = link.closest('article, li, [role="listitem"], [data-testid*="result"], .result, .record') || link.parentElement;
    const text = clean(box?.innerText || link.innerText || "");
    const title = clean(link.innerText) || pickTextAfter(text, ["Title"]);
    if (!title || title.length < 5) continue;

    const params = url.searchParams;
    const db = params.get("db") || urlDb;
    const accessionNumber = params.get("AN") || params.get("an") || (text.match(/Accession Number[:\s]+([A-Z0-9-]+)/i)?.[1] || "");
    const detailId = url.pathname.match(/\/search\/details\/([^/?#]+)/)?.[1] || "";
    const doi = (text.match(/\b10\.\d{4,9}\/[-._;()/:A-Z0-9]+/i)?.[0] || "").replace(/[.,;)]$/, "");
    const pmid = text.match(/PMID[:\s]+(\d+)/i)?.[1] || "";
    const source = pickTextAfter(text, ["Source", "Journal", "Publication", "Published in"]) || "";
    const date = pickTextAfter(text, ["Publication Date", "Date", "Published"]) || (text.match(/\b(19|20)\d{2}\b/)?.[0] || "");
    const authors = uniq([...box.querySelectorAll('a[href*="AU="], button, [data-testid*="author"]')]
      .map(el => clean(el.innerText))
      .filter(v => v && v.length < 120 && !/full text|pdf|access|cite|save|share/i.test(v)));
    const fullText = /pdf full text|html full text|access now|full text/i.test(text);

    records.push({ rank: records.length + 1, title, authors, source, date, doi, pmid, accessionNumber, detailId, db, fullText, url: key });
  }

  const pageText = clean(document.body?.innerText || "");
  const totalResults = pageText.match(/([\d,]+)\s+results?/i)?.[0] || "";
  return { records, totalResults, currentUrl: location.href };
}
```

Return the JSON. If `records` is empty, check whether login, filters, or delayed loading are responsible before concluding there are no results.
