---
name: cinahl-navigate-pages
description: Navigate CINAHL/EBSCOhost search result pages, change sort order, and re-parse the current results.
argument-hint: "[next|prev|page N|sort newest|sort relevance|show 50]"
---

# CINAHL Result Navigation

Move around an EBSCOhost/CINAHL result list while preserving the current authenticated session.

## Supported Requests

- `next`: go to next result page
- `prev`: go to previous result page
- `page N`: jump to a visible page number when the pagination control exposes it
- `sort newest`: sort by date newest first
- `sort relevance`: sort by relevance
- `show 25`, `show 50`: change result count when the UI exposes a result-count menu

## Steps

### Step 1: Confirm Current Page

Use `evaluate_script`:

```javascript
() => ({
  url: location.href,
  title: document.title,
  text: (document.body?.innerText || "").slice(0, 1000),
  onResults: /\/search/.test(location.href) && /result|records?|search/i.test(document.body?.innerText || "")
})
```

If not on CINAHL/EBSCOhost results, ask the user to run `cinahl-search` or navigate to a result page first.

### Step 2: Perform Navigation Or Sort

Use DOM controls because EBSCO pagination and sort parameters vary by institution and interface version:

```javascript
(command) => {
  const clean = s => (s || "").replace(/\s+/g, " ").trim();
  const all = [...document.querySelectorAll('a, button, [role="button"], select')];
  const visible = el => !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
  const label = el => clean(el.innerText || el.getAttribute("aria-label") || el.getAttribute("title") || el.value);
  const low = command.toLowerCase();

  const clickFirst = patterns => {
    for (const el of all) {
      const text = label(el);
      if (!text || !visible(el)) continue;
      if (patterns.some(re => re.test(text))) {
        el.click();
        return { clicked: text };
      }
    }
    return null;
  };

  if (/^next/.test(low)) return clickFirst([/next/i, /下一页|后一页/]) || { error: "Next control not found" };
  if (/^prev|previous|back/.test(low)) return clickFirst([/previous/i, /prev/i, /上一页|前一页/]) || { error: "Previous control not found" };

  const page = low.match(/page\s+(\d+)/)?.[1] || low.match(/^(\d+)$/)?.[1];
  if (page) return clickFirst([new RegExp("^" + page + "$")]) || { error: "Page control not found: " + page };

  if (/newest|date|recent/.test(low)) return clickFirst([/newest/i, /date/i, /most recent/i, /publication date/i]) || { error: "Date sort control not found" };
  if (/relevance|relevant/.test(low)) return clickFirst([/relevance/i, /most relevant/i]) || { error: "Relevance sort control not found" };

  const show = low.match(/show\s+(25|50|100)/)?.[1];
  if (show) return clickFirst([new RegExp(show + "\\s*(results|per page|items)?", "i")]) || { error: "Result-count control not found: " + show };

  return { error: "Unknown navigation command: " + command };
}
```

Pass `$ARGUMENTS` as `command`.

### Step 3: Re-Parse Results

Wait briefly with `evaluate_script`, then call the same extraction logic as `cinahl-parse-results`.

```javascript
async () => {
  await new Promise(r => setTimeout(r, 1500));
  return { url: location.href, title: document.title };
}
```

Then run `cinahl-parse-results`.

## Notes

- If the first click opens a menu rather than applying the action, take a fresh snapshot and click the newly visible option.
- Do not open a new tab unless the user asks for multi-page collection.
