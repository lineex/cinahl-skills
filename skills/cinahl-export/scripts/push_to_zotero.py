#!/usr/bin/env python3
"""Push CINAHL/EBSCOhost citations to Zotero through the local Connector API.

Supported modes:
  1. RIS import: --ris-file or --ris-data
  2. JSON import: --json, containing one record or a list of records

The script uses deterministic session IDs so repeated imports of the same
content are idempotent. Zotero may return 409 for an existing session; that is
treated as success because it means the item was already submitted.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

ZOTERO_API = "http://127.0.0.1:23119/connector"
HTTP_TIMEOUT = 15


def make_session_id(content_key: str) -> str:
    return hashlib.md5(content_key.encode("utf-8", errors="surrogateescape")).hexdigest()[:12]


def zotero_request(endpoint: str, data: Any | None = None, timeout: int = HTTP_TIMEOUT) -> tuple[int, Any | None]:
    url = f"{ZOTERO_API}/{endpoint}"
    body = json.dumps(data or {}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Zotero-Connector-API-Version": "3",
        },
    )
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        text = resp.read().decode("utf-8", errors="replace")
        return resp.status, json.loads(text) if text else None
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        try:
            return exc.code, json.loads(text) if text else None
        except json.JSONDecodeError:
            return exc.code, {"error": text}
    except urllib.error.URLError:
        return 0, None
    except TimeoutError:
        return -1, {"error": f"Request timed out ({timeout}s)"}


def push_ris(ris_data: str) -> dict[str, Any]:
    ris_data = ris_data.strip()
    if not ris_data:
        return {"success": False, "message": "Empty RIS data."}

    session_id = make_session_id(ris_data)
    url = f"{ZOTERO_API}/import?session={session_id}"
    payload = json.dumps(ris_data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Zotero-Connector-API-Version": "3",
        },
    )

    try:
        resp = urllib.request.urlopen(req, timeout=HTTP_TIMEOUT)
        body = resp.read().decode("utf-8", errors="replace")
        return {"success": True, "message": f"Saved to Zotero (session: {session_id}). Response: {body}"}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        if exc.code == 409:
            return {"success": True, "message": f"Already saved, no duplicates added (session: {session_id})."}
        return {"success": False, "message": f"HTTP {exc.code}: {body}"}
    except urllib.error.URLError as exc:
        return {
            "success": False,
            "message": f"Cannot connect to Zotero. Is Zotero desktop running? Error: {exc.reason}",
        }
    except TimeoutError:
        return {"success": False, "message": f"Request timed out ({HTTP_TIMEOUT}s)."}


def as_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [v.strip() for v in re.split(r"\s*;\s*|\s*\|\s*", str(value)) if v.strip()]


def year_from_date(value: str) -> str:
    match = re.search(r"\b(18|19|20)\d{2}\b", value or "")
    return match.group(0) if match else value


def split_pages(pages: str) -> tuple[str, str]:
    if not pages:
        return "", ""
    match = re.search(r"(\w+)\s*[-–]\s*(\w+)", pages)
    if match:
        return match.group(1), match.group(2)
    return pages, ""


def build_extra(record: dict[str, Any]) -> str:
    extras = []
    for key, label in [
        ("accessionNumber", "CINAHL AN"),
        ("db", "EBSCO Database"),
        ("pmid", "PMID"),
        ("documentType", "Document Type"),
        ("language", "Language"),
    ]:
        value = record.get(key)
        if value:
            extras.append(f"{label}: {value}")
    return "\n".join(extras)


def build_zotero_item(record: dict[str, Any], item_id: str) -> dict[str, Any]:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    pages = str(record.get("pages", "") or "")
    start_page, end_page = split_pages(pages)
    item = {
        "id": item_id,
        "itemType": "journalArticle",
        "title": record.get("title", ""),
        "creators": [{"name": author, "creatorType": "author"} for author in as_list(record.get("authors"))],
        "abstractNote": record.get("abstract", ""),
        "publicationTitle": record.get("source", "") or record.get("journal", ""),
        "date": year_from_date(str(record.get("date", "") or "")),
        "volume": record.get("volume", ""),
        "issue": record.get("issue", ""),
        "pages": pages,
        "DOI": record.get("doi", ""),
        "url": record.get("url", ""),
        "ISSN": record.get("issn", ""),
        "libraryCatalog": "CINAHL (EBSCOhost)",
        "accessDate": now,
        "extra": build_extra(record),
        "tags": [{"tag": subject, "type": 1} for subject in as_list(record.get("subjects"))],
    }
    if start_page and end_page and not item["pages"]:
        item["pages"] = f"{start_page}-{end_page}"
    return {k: v for k, v in item.items() if v not in ("", [], None)}


def load_json_records(path: str) -> list[dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "records" in data:
        return data["records"]
    if isinstance(data, dict) and "items" in data:
        return data["items"]
    if isinstance(data, dict):
        return [data]
    raise ValueError("JSON input must be an object, a list, or an object with records/items.")


def save_items(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        return {"success": False, "message": "No records to save."}

    key = "|".join(sorted(str(r.get("title", "")) + str(r.get("accessionNumber", "")) for r in records))
    session_id = make_session_id(key)
    items = []
    for i, record in enumerate(records):
        if record.get("itemType"):
            item = dict(record)
            item.setdefault("id", f"cinahl_{session_id}_{i}")
        else:
            item = build_zotero_item(record, f"cinahl_{session_id}_{i}")
        items.append(item)

    uri = records[0].get("url", "") if isinstance(records[0], dict) else ""
    status, data = zotero_request("saveItems", {"sessionID": session_id, "uri": uri, "items": items})

    if status == 201:
        return {"success": True, "message": f"Saved to Zotero (session: {session_id}).", "count": len(items)}
    if status == 409:
        return {"success": True, "message": f"Already saved, no duplicates added (session: {session_id}).", "count": len(items)}
    if status == 0:
        return {"success": False, "message": "Zotero is not running or connection refused."}
    if status == -1:
        return {"success": False, "message": "Request to Zotero timed out."}
    return {"success": False, "message": f"Zotero returned HTTP {status}: {data}"}


def list_selected_collection() -> None:
    status, data = zotero_request("getSelectedCollection")
    if status == 0:
        print("Error: Zotero is not running.")
        sys.exit(1)
    if status != 200 or not data:
        print(f"Could not read selected collection. HTTP {status}: {data}")
        sys.exit(1)
    print(f"Current collection: {data.get('name', '?')} (ID: {data.get('id', '?')})")
    print(f"Library: {data.get('libraryName', '?')}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Push CINAHL/EBSCOhost citations to Zotero.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ris-file", help="Path to an RIS file.")
    group.add_argument("--ris-data", help="RIS data string.")
    group.add_argument("--json", help="Path to JSON citation data.")
    group.add_argument("--list", action="store_true", help="Show the selected Zotero collection.")
    args = parser.parse_args()

    if args.list:
        list_selected_collection()
        return 0

    if args.ris_file:
        result = push_ris(Path(args.ris_file).read_text(encoding="utf-8"))
    elif args.ris_data:
        result = push_ris(args.ris_data)
    else:
        result = save_items(load_json_records(args.json))

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    raise SystemExit(main())
