"""
Error Cache — Content-Addressed AI Solution Cache
==================================================
Stores AI-generated solutions keyed by a normalized error fingerprint (hash).
The same error, regardless of file path, line number, or machine, always maps
to the same fingerprint — enabling cross-project, cross-session cache hits.

Cache file: ~/.ai-logmaster/error_cache.json
"""
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


# ── Constants ────────────────────────────────────────────────────────────────
CACHE_DIR = Path.home() / ".ai-logmaster"
CACHE_FILE = CACHE_DIR / "error_cache.json"

# All Python (and common) exception class names to identify the error line
_KNOWN_EXCEPTIONS = [
    "modulenotfounderror", "importerror",
    "typeerror", "valueerror", "keyerror", "indexerror",
    "attributeerror", "nameerror", "runtimeerror",
    "filenotfounderror", "permissionerror",
    "connectionerror", "connectionrefusederror", "timeouterror",
    "syntaxerror", "indentationerror",
    "zerodivisionerror", "overflowerror", "memoryerror",
    "recursionerror", "stopiteration", "assertionerror",
    "notimplementederror", "oserror", "ioerror",
    # Node / JS style (for multi-language support)
    "typeerror", "referenceerror", "syntaxerror",
    "error:", "exception:",
]


class ErrorCache:
    """
    Content-addressed, persistent key-value cache for AI error solutions.

    Flow:
        1. Normalize error (strip paths, line numbers, addresses)
        2. Extract error signature (the canonical exception line)
        3. MD5 hash → 8-char hex fingerprint
        4. Lookup / store in ~/.ai-logmaster/error_cache.json
    """

    def __init__(self):
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self._data: Dict[str, dict] = self._load()

    # ── Public API ────────────────────────────────────────────────────────────

    def get(self, error_context: str) -> Optional[Dict]:
        """
        Look up a cached solution for the given error context.

        Returns the cached result dict (with 'type', 'cause', 'fixes', ...)
        or None on a miss.
        """
        fingerprint = self._fingerprint(error_context)
        entry = self._data.get(fingerprint)
        if entry:
            # Update hit stats
            entry["hits"] = entry.get("hits", 0) + 1
            entry["last_seen"] = datetime.now().isoformat(timespec="seconds")
            self._save()
            return {
                "type": entry["type"],
                "cause": entry["cause"],
                "fixes": entry["fixes"],
                "confidence": entry.get("confidence", 0.95),
                "method": "AI (Cached — 0 API calls)",
                "cache_hit": True,
                "fingerprint": fingerprint,
            }
        return None

    def store(self, error_context: str, result: Dict) -> str:
        """
        Persist an AI-generated result for this error context.

        Returns the fingerprint that was used as the cache key.
        """
        fingerprint = self._fingerprint(error_context)
        signature = self._extract_signature(self._normalize(error_context))

        self._data[fingerprint] = {
            "fingerprint": fingerprint,
            "error_signature": signature,
            "type": result.get("type", "Unknown"),
            "cause": result.get("cause", ""),
            "fixes": result.get("fixes", []),
            "confidence": result.get("confidence", 0.90),
            "hits": 0,
            "first_seen": datetime.now().isoformat(timespec="seconds"),
            "last_seen": datetime.now().isoformat(timespec="seconds"),
        }
        self._save()
        return fingerprint

    def clear(self) -> int:
        """Delete all cached entries. Returns the number of entries cleared."""
        count = len(self._data)
        self._data = {}
        self._save()
        return count

    def stats(self) -> Dict:
        """Return summary statistics about the cache."""
        total = len(self._data)
        total_hits = sum(e.get("hits", 0) for e in self._data.values())
        size_bytes = CACHE_FILE.stat().st_size if CACHE_FILE.exists() else 0
        entries = [
            {
                "fingerprint": fp,
                "error_signature": e.get("error_signature", ""),
                "type": e.get("type", ""),
                "hits": e.get("hits", 0),
                "first_seen": e.get("first_seen", ""),
                "last_seen": e.get("last_seen", ""),
            }
            for fp, e in sorted(
                self._data.items(),
                key=lambda x: x[1].get("hits", 0),
                reverse=True,
            )
        ]
        return {
            "total_entries": total,
            "total_hits": total_hits,
            "size_bytes": size_bytes,
            "cache_path": str(CACHE_FILE),
            "entries": entries,
        }

    # ── Fingerprinting ────────────────────────────────────────────────────────

    def _fingerprint(self, error_context: str) -> str:
        """Normalize → extract signature → MD5 hash → 8-char key."""
        normalized = self._normalize(error_context)
        signature = self._extract_signature(normalized)
        return hashlib.md5(signature.encode("utf-8")).hexdigest()[:8]

    def _normalize(self, text: str) -> str:
        """
        Strip all volatile parts from the error context so that the same
        logical error always produces the same normalized string regardless
        of machine, file path, or line number.
        """
        # 1. Remove Python traceback file lines:
        #    File "/home/user/app.py", line 42, in <module>
        text = re.sub(r'File ".*?",\s*line\s*\d+[^\n]*', "", text)

        # 2. Remove Windows-style paths  C:\Users\...
        text = re.sub(r'[A-Za-z]:\\[^\s,"\']+', "", text)

        # 3. Remove Unix-style absolute paths  /home/user/...
        text = re.sub(r'/[^\s,"\']+\.py', "", text)

        # 4. Remove memory addresses  0x7f3a1b2c
        text = re.sub(r"0x[0-9a-fA-F]+", "", text)

        # 5. Remove timestamps  2026-08-09 02:00:00
        text = re.sub(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", "", text)

        # 6. Remove standalone line numbers / port numbers / exit codes
        #    but NOT numbers that are part of a word like 'pydantic>=2.0'
        text = re.sub(r"(?<!\w)\d+(?!\w)", "", text)

        # 7. Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text.lower()

    def _extract_signature(self, normalized: str) -> str:
        """
        Pull out the canonical exception line from the normalized text.
        This is the most stable, unique, and compact key.

        Example:
          normalized = "traceback ... modulenotfounderror: no module named 'pydantic'"
          returns    = "modulenotfounderror: no module named 'pydantic'"
        """
        # Try to find a line containing a known exception class name
        lines = [l.strip() for l in normalized.split(".") if l.strip()]
        for line in reversed(lines):
            line_lower = line.lower()
            if any(exc in line_lower for exc in _KNOWN_EXCEPTIONS):
                return line.strip()

        # Fallback: look for any line with "error:" or "exception:"
        for line in reversed(normalized.split("\n")):
            line = line.strip()
            if "error:" in line.lower() or "exception:" in line.lower():
                return line

        # Last resort: first 200 chars of the normalized text
        return normalized[:200]

    # ── Persistence ───────────────────────────────────────────────────────────

    def _load(self) -> Dict[str, dict]:
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                print("[ERROR_CACHE] Cache file corrupted — starting fresh.")
        return {}

    def _save(self) -> None:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)
