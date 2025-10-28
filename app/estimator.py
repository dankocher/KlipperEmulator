import math, re
from pathlib import Path

def estimate_time(printer_cfg: str,
                  gcode_path: str,
                  *,
                  speed_factor: float = 1.0,
                  flow_factor: float = 1.0,
                  max_velocity: float = 300.0,
                  max_accel: float = 5000.0,
                  square_corner_velocity: float = 5.0,
                  accel_to_decel: float = 2500.0,
                  pressure_advance: float = 0.0,
                  smooth_time: float = 0.04) -> dict:
    """
    Simulación aproximada del tiempo de impresión basada en movimientos G1.
    No usa Klipper real, pero considera velocidad, aceleración y aceleración a desaceleración.
    """

    path = Path(gcode_path)
    if not path.exists():
        return {"ok": False, "error": "Archivo G-code no encontrado"}

    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    last = {"X": 0.0, "Y": 0.0, "Z": 0.0, "E": 0.0}
    total_time = 0.0
    feed = 0.0
    regex = re.compile(r"([XYZEFR])([-+]?\d*\.?\d+)")
    for ln in lines:
        ln = ln.strip()
        if not ln or ln.startswith(";"): continue
        if not (ln.startswith("G1") or ln.startswith("G0")): continue
        params = dict((m.group(1), float(m.group(2))) for m in regex.finditer(ln))
        if "F" in params:
            feed = params["F"] / 60.0  # mm/s
        if any(k in params for k in ["X", "Y", "Z"]):
            x = params.get("X", last["X"])
            y = params.get("Y", last["Y"])
            z = params.get("Z", last["Z"])
            dist = math.sqrt((x - last["X"]) ** 2 + (y - last["Y"]) ** 2 + (z - last["Z"]) ** 2)
            last.update({"X": x, "Y": y, "Z": z})

            # velocidad objetivo considerando multiplicador
            v = min(feed * speed_factor, max_velocity)
            if v <= 0: continue

            # tiempo de aceleración + tramo constante + desaceleración
            a = max_accel
            t_accel = v / a
            d_accel = 0.5 * a * t_accel**2
            if dist < 2 * d_accel:
                # no llega a velocidad máxima (trayecto corto)
                t = 2 * math.sqrt(dist / a)
            else:
                d_const = dist - 2 * d_accel
                t = 2 * t_accel + d_const / v

            total_time += t

    return {"ok": True, "seconds": total_time, "raw": f"Simulación interna: {total_time:.1f} s"}
