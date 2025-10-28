import re, base64
from pathlib import Path

def extract_thumbnail(gcode_path: str, out_png_path: str, target_size: int = 300) -> bool:
    """
    Extrae el thumbnail de un G-code generado por Cura o Prusa.
    Prioriza el de tamaño indicado (por defecto 300x300).
    Si no lo encuentra, usa el más grande disponible.
    """
    p = Path(gcode_path)
    if not p.exists():
        return False

    data = p.read_text(encoding="utf-8", errors="ignore").splitlines()

    # Buscar bloques de miniaturas
    thumbs = []
    current = None
    current_size = None

    for line in data:
        if line.startswith("; thumbnail begin"):
            # Ejemplo: "; thumbnail begin 300*300"
            m = re.search(r"(\d+)\*(\d+)", line)
            if m:
                current_size = int(m.group(1))
            else:
                current_size = 0
            current = []
            continue
        if line.startswith("; thumbnail end"):
            if current:
                thumbs.append((current_size, current))
            current = None
            current_size = None
            continue
        if current is not None:
            if line.startswith("; "):
                current.append(line[2:].strip())
            elif line.startswith(";"):
                current.append(line[1:].strip())

    # Si no hay thumbnails
    if not thumbs:
        return False

    # Ordenar por tamaño
    thumbs.sort(key=lambda x: x[0], reverse=True)

    # Buscar el del tamaño solicitado (p. ej. 300x300)
    selected = None
    for size, lines in thumbs:
        if size == target_size:
            selected = (size, lines)
            break

    # Si no existe exactamente ese tamaño, usar el más grande
    if selected is None:
        selected = thumbs[0]

    # Decodificar a PNG
    try:
        raw = "".join(selected[1])
        png = base64.b64decode(raw)
        Path(out_png_path).write_bytes(png)
        return True
    except Exception as e:
        print(f"⚠️ Error al decodificar thumbnail: {e}")
        return False
