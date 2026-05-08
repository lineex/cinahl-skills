---
name: cinahl-download
description: Download accessible full text from CINAHL/EBSCOhost records. Requires institutional access and only works when the record exposes PDF or HTML full text.
argument-hint: "[AN=accessionNumber db=ccm|rzh|cul|cin20|c8h or details URL]"
disable-model-invocation: true
---

# CINAHL Full-Text Download

Download accessible CINAHL/EBSCOhost full text or open the best available full-text route.

## Prerequisites

- The user must have legitimate access through their institution, subscription, or open-access links.
- Do not bypass paywalls or authentication.
- If the record only exposes a link resolver or publisher link, open that link and report that direct EBSCO PDF is unavailable.

## Steps

### Step 1: Open The Record

If not already on the detail page, use `cinahl-paper-detail` navigation rules:

```text
https://search.ebscohost.com/login.aspx?direct=true&db={DB}&AN={AN}&site=ehost-live&scope=site
```

or open the supplied details URL. Include the webdriver-hiding `initScript`.

### Step 2: Find Full-Text Links

Use:

```javascript
async () => {
  for (let i = 0; i < 24; i++) {
    if ([...document.querySelectorAll('a, button')].some(el => /pdf|html full text|access now|full text/i.test(el.innerText || el.getAttribute('aria-label') || el.href || ""))) break;
    await new Promise(r => setTimeout(r, 500));
  }
  const clean = s => (s || "").replace(/\s+/g, " ").trim();
  const links = [...document.querySelectorAll('a, button')]
    .map(el => ({
      label: clean(el.innerText || el.getAttribute("aria-label") || el.getAttribute("title")),
      href: el.href || "",
      tag: el.tagName
    }))
    .filter(x => /pdf|html full text|access now|full text|link resolver|find it|publisher/i.test(x.label + " " + x.href));

  const pdf = links.find(x => /pdf/i.test(x.label + " " + x.href));
  const html = links.find(x => /html full text|html/i.test(x.label + " " + x.href));
  const resolver = links.find(x => /link resolver|find it|access options|publisher|full text/i.test(x.label));
  const title = (document.querySelector("h1")?.innerText || document.title || "cinahl-record").replace(/\s+/g, " ").trim();
  const an = (document.body?.innerText || "").match(/Accession Number[:\s]+([A-Z0-9-]+)/i)?.[1] || "";
  return { pdf, html, resolver, links, title, accessionNumber: an, currentUrl: location.href };
}
```

### Step 3: Open Or Click The Best Link

Priority:

1. PDF link or PDF button
2. HTML full text
3. access options / link resolver / publisher full text

If the best target has `href`, use `navigate_page` to that URL with `initScript`. If it is a button without `href`, take a fresh snapshot and click the matching element.

### Step 4: Trigger Browser Download For PDFs

After a PDF is open, verify:

```javascript
async () => {
  await new Promise(r => setTimeout(r, 3000));
  return {
    contentType: document.contentType,
    title: document.title,
    url: location.href
  };
}
```

If `document.contentType` is `application/pdf` or the URL/title strongly indicates a PDF, run:

```javascript
(filename) => {
  const a = document.createElement("a");
  a.href = location.href;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  return { downloaded: true, filename };
}
```

Use `{DB}-{AN}.pdf` when `AN` is known, otherwise a sanitized title.

### Step 5: Report Outcome

Tell the user exactly which route succeeded:

- PDF downloaded
- HTML full text opened
- link resolver opened
- no full text exposed
- login/authentication required

## Notes

- EBSCOhost often links to publisher PDFs rather than hosting the PDF directly. In that case, the browser may need to follow the publisher's own access workflow.
- If a dialog opens, use a fresh snapshot and click the visible "Download", "PDF", or "Open" control.
