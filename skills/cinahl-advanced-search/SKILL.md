---
name: cinahl-advanced-search
description: Perform advanced CINAHL searches on EBSCOhost using field codes, Boolean syntax, year ranges, and common limiters.
argument-hint: "[terms and filters, e.g. title:falls author:Smith year:2020-2026 fulltext peerreviewed]"
---

# CINAHL Advanced Search

Construct and run an advanced CINAHL query on EBSCOhost.

## Field Code Map

Map natural-language filters to EBSCO/CINAHL field codes:

| User intent | EBSCO query |
| --- | --- |
| title | `TI {term}` |
| abstract | `AB {term}` |
| title or abstract | `(TI {term} OR AB {term})` |
| subject / CINAHL heading | `SU {term}` |
| author | `AU {term}` |
| journal / source | `SO {term}` |
| affiliation | `AF {term}` |
| all text | `TX {term}` |

Preserve existing user-provided field codes. Do not rewrite a precise systematic-search string unless the user asks.

## Common Limiters

Use URL parameters for the stable parts:

```text
db={CINAHL_DB}
q={BOOLEAN_QUERY}
searchMode=boolean
limiters=None
```

For institution-specific filters whose URL representation is unstable, navigate first, then use the page controls if exposed:

- full text
- peer reviewed
- publication date range
- academic journals
- evidence-based practice
- research article
- language
- age group

If the requested limiter cannot be applied programmatically, state that the Boolean query has been run and that the visible EBSCO filter should be applied manually.

## Steps

### Step 1: Parse `$ARGUMENTS`

Examples:

```text
title:falls author:Smith year:2020-2026
```

becomes:

```text
TI falls AND AU Smith
```

Then apply the year range using the filter UI when possible. If the user provides a full Boolean query such as:

```text
((TI "pressure injur*" OR AB "pressure injur*") AND (SU nursing OR SU "critical care"))
```

use it unchanged.

### Step 2: Navigate

Use:

```text
{EBSCO_BASE}/search/results?q={BOOLEAN_QUERY}&autocorrect=y&db={CINAHL_DB}&expanders=concept&limiters=None&searchMode=boolean&searchSegment=all-results
```

Always include:

```text
initScript: "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
```

### Step 3: Apply Visible Limiters When Requested

If the results are not fetched and the page remains on the search form, fill the search textbox with `{BOOLEAN_QUERY}` and click Search once before applying filters.

Use `evaluate_script` to click accessible controls by text:

```javascript
(requested) => {
  const want = s => requested.some(x => s.toLowerCase().includes(x));
  const buttons = [...document.querySelectorAll('button, a, label, input')];
  const clicked = [];
  for (const el of buttons) {
    const text = (el.innerText || el.getAttribute('aria-label') || el.value || "").trim();
    const low = text.toLowerCase();
    if (!text) continue;
    if ((want("fulltext") && /full text|全文/i.test(low)) ||
        (want("peerreviewed") && /peer reviewed|scholarly/i.test(low)) ||
        (want("academic") && /academic journal/i.test(low)) ||
        (want("evidence") && /evidence-based practice/i.test(low))) {
      try { el.click(); clicked.push(text); } catch {}
    }
  }
  return { clicked };
}
```

Pass normalized requested limiter names as `args`, for example `["fulltext", "peerreviewed"]`.

### Step 4: Extract Results

Use the same extraction pattern as `cinahl-search`: collect links containing `/search/details/` or classic direct links with `AN=`, deduplicate, and return records with title, authors, source, date, DOI, PMID, `db`, accession number, full-text flag, and detail URL.

### Step 5: Present Results

Show the exact final Boolean query first:

```text
Query: {BOOLEAN_QUERY}
Database: {CINAHL_DB}
Applied visible filters: {clicked filter names}
Found {totalResults}
```

Then present numbered records in the same format as `cinahl-search`.

## Notes

- For systematic-review work, do not silently simplify the query. Exact syntax matters.
- CINAHL/EBSCO truncation and wildcard rules may change; if a user relies on single-letter roots or unusual wildcards, keep the original query and report any on-page EBSCO warning.
