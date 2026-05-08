---
name: cinahl-paper-detail
description: Extract detailed metadata from a CINAHL/EBSCOhost article record by accession number, detail URL, or current page.
argument-hint: "[AN=accessionNumber db=ccm|rzh|cul|cin20|c8h or details URL]"
---

# CINAHL Article Detail

Open or inspect a CINAHL/EBSCOhost article record and return structured metadata.

## Accepted Inputs

- Current browser page is already an EBSCOhost article detail page.
- New EBSCOhost details URL:

```text
https://research.ebsco.com/c/{profile}/search/details/{recordId}?db={db}&limiters=None&q={query}&searchMode=boolean
```

- Classic direct accession-number link:

```text
AN=181230979 db=rzh
```

## Steps

### Step 1: Navigate If Needed

If `$ARGUMENTS` contains a full URL, navigate to it.

If `$ARGUMENTS` contains `AN=...`, build:

```text
https://search.ebscohost.com/login.aspx?direct=true&db={DB}&AN={AN}&site=ehost-live&scope=site
```

Use the current `CINAHL_DB` when no `db=` is supplied. Always include:

```text
initScript: "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
```

If the current page is already a detail page, skip navigation.

### Step 2: Check Access

If the page redirects to institution login, SSO, Shibboleth, EZProxy, WebVPN, or an institution picker, tell the user:

```text
页面被重定向，请在浏览器中完成登录或机构认证后告知我。
```

If the record says the user is not assigned or not authorized, report the access limitation and keep the canonical URL/AN visible.

### Step 3: Extract Metadata

Use one `evaluate_script` call:

```javascript
async () => {
  for (let i = 0; i < 24; i++) {
    if (document.querySelector('h1, [data-testid*="title"], a[href*="doi.org"], a[href*="pdf"], button')) break;
    await new Promise(r => setTimeout(r, 500));
  }

  const clean = s => (s || "").replace(/\s+/g, " ").trim();
  const text = document.body?.innerText || "";
  const lines = text.split(/\n+/).map(clean).filter(Boolean);
  const pickLineAfter = labels => {
    for (const label of labels) {
      const idx = lines.findIndex(l => new RegExp("^" + label + "\\b", "i").test(l));
      if (idx >= 0) {
        const same = lines[idx].replace(new RegExp("^" + label + "\\s*:?\\s*", "i"), "");
        if (same && same !== lines[idx]) return clean(same);
        if (lines[idx + 1]) return lines[idx + 1];
      }
    }
    return "";
  };
  const collectSection = labels => {
    const start = lines.findIndex(l => labels.some(label => new RegExp("^" + label + "\\b", "i").test(l)));
    if (start < 0) return "";
    const stopLabels = /^(subjects?|subject terms|authors?|source|journal|publication|issn|isbn|doi|pmid|accession|language|database|full text|references?|cite|export)\b/i;
    const out = [];
    for (let i = start + 1; i < lines.length && out.length < 40; i++) {
      if (stopLabels.test(lines[i]) && out.length) break;
      out.push(lines[i]);
    }
    return clean(out.join(" "));
  };
  const splitList = value => value.split(/\s*;\s*|\s*,\s*(?=[A-Z][A-Za-z'\-]+(?:\s+[A-Z]\.?|$))/).map(clean).filter(Boolean);

  const url = location.href;
  const current = new URL(url);
  const title = clean(document.querySelector('h1')?.innerText)
    || clean(document.querySelector('[data-testid*="title"]')?.innerText)
    || pickLineAfter(["Title"]);
  const doi = (text.match(/\b10\.\d{4,9}\/[-._;()/:A-Z0-9]+/i)?.[0] || "").replace(/[.,;)]$/, "");
  const pmid = text.match(/PMID[:\s]+(\d+)/i)?.[1] || pickLineAfter(["PMID"]);
  const accessionNumber = current.searchParams.get("AN")
    || current.searchParams.get("an")
    || text.match(/Accession Number[:\s]+([A-Z0-9-]+)/i)?.[1]
    || pickLineAfter(["Accession Number"]);
  const db = current.searchParams.get("db") || pickLineAfter(["Database"]);
  const source = pickLineAfter(["Source", "Journal", "Publication", "Publication Title"]);
  const date = pickLineAfter(["Publication Date", "Date Published", "Published"]);
  const volume = pickLineAfter(["Volume"]);
  const issue = pickLineAfter(["Issue"]);
  const pages = pickLineAfter(["Pages", "Start Page"]);
  const issn = pickLineAfter(["ISSN"]);
  const language = pickLineAfter(["Language"]);
  const documentType = pickLineAfter(["Document Type", "Publication Type"]);
  const abstract = collectSection(["Abstract"]);
  const subjects = splitList(collectSection(["Subjects", "Subject Terms", "CINAHL Headings"]));
  const authorText = pickLineAfter(["Authors", "Author"]);
  const authors = splitList(authorText).filter(a => a.length < 120);

  const accessLinks = [...document.querySelectorAll('a, button')]
    .map(el => ({
      label: clean(el.innerText || el.getAttribute("aria-label") || el.getAttribute("title")),
      href: el.href || ""
    }))
    .filter(x => x.label && /pdf|html full text|full text|access|link resolver|find it|doi|publisher/i.test(x.label + " " + x.href));

  return {
    title,
    authors,
    source,
    date,
    volume,
    issue,
    pages,
    issn,
    doi,
    pmid,
    accessionNumber,
    db,
    language,
    documentType,
    abstract,
    subjects,
    accessLinks,
    url
  };
}
```

### Step 4: Present The Record

Return a compact record:

```text
{title}
Authors: ...
Source: journal, year, volume(issue), pages
DOI: ...
PMID: ...
DB/AN: ...
Document type: ...
Subjects: ...
Abstract: ...
Full-text links: PDF / HTML / link resolver / publisher
```

## Notes

- CINAHL subject headings are important; include them when exposed.
- If the page exposes only a publisher link, do not claim the PDF is available.
- Preserve the detail URL so `cinahl-export` or `cinahl-download` can reuse the same authenticated session.
