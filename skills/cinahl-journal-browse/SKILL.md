---
name: cinahl-journal-browse
description: Browse CINAHL/EBSCOhost publications or search within a journal/source title.
argument-hint: "[journal or publication name]"
---

# CINAHL Journal Browse

Find CINAHL publication pages and recent records for a journal or source title.

## Strategy

EBSCOhost institution profiles expose publication pages differently. Try these routes in order:

1. New EBSCOhost publication search:

```text
{EBSCO_BASE}/search/advanced/publications?db={CINAHL_DB}&q={JOURNAL}
```

2. Source-title search fallback:

```text
{EBSCO_BASE}/search/results?q=SO%20{JOURNAL}&autocorrect=y&db={CINAHL_DB}&expanders=concept&limiters=None&searchMode=boolean&searchSegment=all-results
```

3. If the user provides a direct `/search/advanced/publications/{id}` URL, open it unchanged.

Always include:

```text
initScript: "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
```

## Steps

### Step 1: Navigate

Use the publication-search URL when `EBSCO_BASE` is known. If it returns no obvious publication controls after loading, immediately fall back to `SO {journal}` search.

### Step 2: Extract Publication Matches

Use:

```javascript
async () => {
  for (let i = 0; i < 20; i++) {
    if (document.querySelector('a[href*="/publications/"], a[href*="/search/details/"]')) break;
    await new Promise(r => setTimeout(r, 500));
  }
  const clean = s => (s || "").replace(/\s+/g, " ").trim();
  const links = [...document.querySelectorAll('a[href*="/publications/"], a[href*="/search/advanced/publications/"]')];
  const publications = [];
  const seen = new Set();
  for (const a of links) {
    const href = new URL(a.href, location.href).href;
    const title = clean(a.innerText);
    if (!title || seen.has(href)) continue;
    seen.add(href);
    const box = a.closest('article, li, [role="listitem"], .result, .record') || a.parentElement;
    const text = clean(box?.innerText || "");
    publications.push({ title, url: href, details: text });
  }
  return { publications, currentUrl: location.href };
}
```

### Step 3: If No Publication Matches, Parse Source Search Results

Run the same result extraction as `cinahl-parse-results` and present it as recent or matching articles from the source.

### Step 4: Present Results

For publication matches:

```text
1. {publication title}
   {details}
   URL: {url}
```

For source-title search fallback:

```text
No publication-browse page was exposed by this EBSCO profile. Showing records where SO matches {journal}.
```

Then list article records.

## Notes

- Publication browse is more profile-dependent than record search. Source-title search is the robust fallback.
- If the user wants journal holdings or date coverage, extract the publication page text and report coverage exactly as shown.
