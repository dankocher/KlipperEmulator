from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import shutil, math

from .storage import add_file, list_files, delete_file, UPLOADS, THUMBS
from .gcode_thumbnail import extract_thumbnail
from .estimator import estimate_time

app = FastAPI(title="Klipper Time Web")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="templates")

ROOT = Path(".").resolve()
PRINTER_CFG = ROOT / "printer.cfg"

@app.get("/", response_class=HTMLResponse)
def index(req: Request):
    files = list_files()
    return templates.TemplateResponse("index.html", {"request": req, "files": files, "has_cfg": PRINTER_CFG.exists()})

@app.post("/api/upload")
async def upload_gcode(file: UploadFile = File(...)):
    UPLOADS.mkdir(parents=True, exist_ok=True)
    THUMBS.mkdir(parents=True, exist_ok=True)

    dest = UPLOADS / file.filename
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    # intentar extraer thumbnail
    thumb_path = THUMBS / (dest.stem + ".png")
    has_thumb = extract_thumbnail(str(dest), str(thumb_path))
    thumb = str(thumb_path) if has_thumb else None

    # metadatos sencillos
    meta = {"size": dest.stat().st_size}
    item = add_file(file.filename, str(dest), thumb, meta)
    return {"ok": True, "file": item}

@app.get("/api/files")
def api_files():
    return {"files": list_files()}

@app.delete("/api/files/{file_id}")
def api_delete(file_id: str):
    removed = delete_file(file_id)
    return {"ok": removed is not None}

@app.get("/thumb/{file_id}")
def thumb(file_id: str):
    for it in list_files():
        if it["id"] == file_id and it.get("thumb"):
            return FileResponse(it["thumb"])
    return JSONResponse({"ok": False, "error": "No thumbnail"}, status_code=404)

@app.post("/api/estimate")
async def api_estimate(
    file_id: str = Form(...),
    speed_percent: float = Form(100.0),
    flow_percent: float = Form(150.0),
    max_velocity: float = Form(300.0),
    max_accel: float = Form(5000.0),
    square_corner_velocity: float = Form(5.0),
    accel_to_decel: float = Form(2500.0),
    pressure_advance: float = Form(0.0),
    smooth_time: float = Form(0.04),
):
    if not PRINTER_CFG.exists():
        return JSONResponse({"ok": False, "error": "printer.cfg no encontrado en la raíz"}, status_code=400)

    target = None
    for it in list_files():
        if it["id"] == file_id:
            target = it
            break
    if not target:
        return JSONResponse({"ok": False, "error": "Archivo no encontrado"}, status_code=404)

    res = estimate_time(
        str(PRINTER_CFG),
        target["path"],
        speed_factor=(speed_percent/100.0),
        flow_factor=(flow_percent/100.0),
        max_velocity=max_velocity,
        max_accel=max_accel,
        square_corner_velocity=square_corner_velocity,
        accel_to_decel=accel_to_decel,
        pressure_advance=pressure_advance,
        smooth_time=smooth_time
    )

    seconds = res.get("seconds")
    pretty = _fmt_time(seconds) if seconds else "N/A"
    return {
        "ok": res.get("ok", False),
        "seconds": seconds,
        "pretty": pretty,
        "raw": res.get("raw", "")
    }

def _fmt_time(s: float|None) -> str:
    if not s: return "N/A"
    s = int(round(s))
    h = s // 3600
    m = (s % 3600)//60
    sec = s % 60
    if h: return f"{h}h {m}m {sec}s"
    if m: return f"{m}m {sec}s"
    return f"{sec}s"
