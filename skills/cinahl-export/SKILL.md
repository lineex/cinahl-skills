---
name: cinahl-export
description: Export CINAHL/EBSCOhost records as RIS, BibTeX, or plain text, and optionally push structured records to Zotero.
argument-hint: "[AN=... db=... format: ris|bibtex|text|zotero or current page/results]"
---

# CINAHL Citation Export

Export CINAHL records from EBSCOhost.

## Supported Inputs

- Current CINAHL detail page.
- Current CINAHL results page.
- One or more identifiers: `AN=181230979 db=rzh`.
- A details URL.
- Optional `format:` value: `ris`, `bibtex`, `text`, or `zotero`. Default: `ris`.

## Export Strategy

1. Prefer EBSCOhost's visible Export/Cite/Share controls when available.
2. If EBSCO's export modal is not exposed or fails, synthesize RIS/BibTeX from `cinahl-paper-detail` or `cinahl-parse-results` metadata.
3. For Zotero, use `scripts/push_to_zotero.py` with RIS or structured JSON.

## Steps

### Step 1: Collect Metadata

If on a detail page, run `cinahl-paper-detail`.

If on a result page, run `cinahl-parse-results` and ask the user which records to export unless the user already supplied ranks or ANs.

If identifiers were supplied, open each record with `cinahl-paper-detail` and collect metadata.

### Step 2: Try EBSCO UI Export

Use a fresh snapshot for visible controls. Common labels:

- `Export`
- `Cite`
- `Share`
- `Save`
- `RIS`
- `Direct Export in RIS Format`
- `BibTeX`

If a modal appears, click the requested format and the final save/export/download control.

If the UI export is successful, tell the user the exported format and filename shown by the browser.

### Step 3: Fallback RIS

When UI export is unavailable, generate RIS:

```text
TY  - JOUR
TI  - {title}
AU  - {author one}
AU  - {author two}
JO  - {source}
PY  - {year}
VL  - {volume}
IS  - {issue}
SP  - {start page}
EP  - {end page}
DO  - {doi}
UR  - {url}
AN  - {accessionNumber}
DB  - CINAHL
N2  - {abstract}
KW  - {subject}
ER  -
```

Write the RIS into `exports/cinahl-export.ris` when file tools are available. If file tools are unavailable in the active environment, return the RIS text directly.

### Step 4: Fallback BibTeX

For `format: bibtex`, generate:

```text
@article{{cinahl-{db}-{accessionNumber}},
  title = {{...}},
  author = {...},
  journal = {...},
  year = {...},
  volume = {...},
  number = {...},
  pages = {...},
  doi = {...},
  url = {...}
}
```

### Step 5: Zotero Push

For `format: zotero`, save RIS or structured JSON and run:

```bash
python skills/cinahl-export/scripts/push_to_zotero.py --ris-file exports/cinahl-export.ris
```

or:

```bash
python skills/cinahl-export/scripts/push_to_zotero.py --json exports/cinahl-export.json
```

Report the script output. If Zotero is not running, tell the user to start Zotero desktop and retry.

## Notes

- Keep `db` and `AN` in every exported item because CINAHL records are often easiest to recover from those fields.
- Do not claim full-text attachment export unless a PDF was actually accessible.
- Export only the records requested by the user; for batch exports from result lists, confirm ranks/ANs before exporting a large set.
