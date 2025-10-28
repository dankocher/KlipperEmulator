import json, time
from pathlib import Path

DATA_DIR = Path("data")
UPLOADS = DATA_DIR / "uploads"
THUMBS  = DATA_DIR / "thumbs"
MANIFEST = DATA_DIR / "manifest.json"

def _load_manifest():
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {"files": []}

def _save_manifest(data):
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def add_file(name:str, path:str, thumb_path:str|None, meta:dict):
    m = _load_manifest()
    file_id = f"{int(time.time()*1000)}"
    item = {
        "id": file_id,
        "name": name,
        "path": path,
        "thumb": thumb_path,
        "meta": meta,
        "ts": int(time.time())
    }
    m["files"].insert(0, item)
    _save_manifest(m)
    return item

def list_files():
    return _load_manifest()["files"]

def delete_file(file_id:str):
    m = _load_manifest()
    keep = []
    removed = None
    for it in m["files"]:
        if it["id"] == file_id:
            removed = it
            try:
                Path(it["path"]).unlink(missing_ok=True)
            except: pass
            if it.get("thumb"):
                try:
                    Path(it["thumb"]).unlink(missing_ok=True)
                except: pass
        else:
            keep.append(it)
    m["files"] = keep
    _save_manifest(m)
    return removed
