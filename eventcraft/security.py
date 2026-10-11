"""Bounded local inputs and credential-free diagnostics."""

import base64
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_PIXELS = 24_000_000


def local_file(value: str | Path, root: Path | None = None) -> Path:
    path = Path(value).expanduser().resolve()
    if root and not path.is_relative_to(root.resolve()):
        raise ValueError("Input path escapes the permitted input root")
    if not path.is_file():
        raise ValueError("Input file does not exist")
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("Input file exceeds the 20 MiB limit")
    return path


def image_uri(value: str | Path, root: Path | None = None) -> str:
    from PIL import Image

    path = local_file(value, root)
    if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        raise ValueError("Only PNG, JPEG and WebP images are accepted")
    with Image.open(path) as im:
        if im.width * im.height > MAX_PIXELS:
            raise ValueError("Image exceeds the 24 megapixel limit")
        im.verify()
    # Raw bytes preserve user QR/logo content; metadata is never copied into logs.
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
    return f"data:{mime[path.suffix.lower()]};base64,{base64.b64encode(path.read_bytes()).decode()}"


def valid_url(value: str) -> bool:
    try:
        parsed = urlsplit(value)
        return bool(
            parsed.scheme in {"https", "http"} and parsed.hostname and "." in parsed.hostname
            and not parsed.username and not parsed.password
            and not any(c.isspace() or ord(c) < 32 for c in value)
            and len(value) <= 2048
        )
    except ValueError:
        return False


def slugify(value: str) -> str:
    clean = re.sub(r"[^\w-]+", "-", value, flags=re.UNICODE).strip("-_")[:70]
    if not clean or clean.upper() in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(10)), *(f"LPT{i}" for i in range(10))}:
        clean = "event-" + hashlib.sha256(value.encode()).hexdigest()[:10]
    return clean


def digest(data: object) -> str:
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
