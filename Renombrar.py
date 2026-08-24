from pathlib import Path
from datetime import datetime
from PIL import Image, ExifTags
import pillow_heif
import os
import csv

RUTA = r"C:\Users\camilo.bolivar_amari\Documents\Mis documentos\Fotos\Fotos"

IMAGENES = {".jpg", ".jpeg", ".heic", ".png"}
VIDEOS = {".mp4", ".mov"}

pillow_heif.register_heif_opener()


def obtener_fecha_exif(ruta_archivo):
    try:
        if ruta_archivo.suffix.lower() in [".jpg", ".jpeg", ".heic"]:
            img = Image.open(ruta_archivo)
            exif = img.getexif()

            for tag_id, valor in exif.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                if tag in (
                    "DateTimeOriginal",
                    "DateTimeDigitized",
                    "DateTime",
                ):
                    if isinstance(valor, bytes):
                        valor = valor.decode(errors='ignore')
                    return datetime.strptime(valor, "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass

    return None


def obtener_fecha_archivo(ruta_archivo):
    return datetime.fromtimestamp(os.path.getmtime(ruta_archivo))


ruta = Path(RUTA)
contador_duplicados = {}

with open(
    "log_renombrado.csv",
    "w",
    newline="",
    encoding="utf-8"
) as log:
    writer = csv.writer(log)
    writer.writerow([
        "Ruta Original",
        "Nombre Original",
        "Nombre Nuevo",
        "Fecha Utilizada"
    ])

    for archivo in ruta.rglob("*"):
        if not archivo.is_file():
            continue

        ext = archivo.suffix.lower()
        if ext not in IMAGENES and ext not in VIDEOS:
            continue

        try:
            fecha = None
            if ext in [".jpg", ".jpeg", ".heic"]:
                fecha = obtener_fecha_exif(archivo)

            if fecha is None:
                fecha = obtener_fecha_archivo(archivo)

            fecha_str = fecha.strftime("%Y%m%d_%H%M%S")
            prefijo = "IMG" if ext in IMAGENES else "VID"
            base_nombre = f"{prefijo}_{fecha_str}"

            consecutivo = contador_duplicados.get(base_nombre, 0) + 1
            contador_duplicados[base_nombre] = consecutivo

            if consecutivo == 1:
                nuevo_nombre = f"{base_nombre}{ext}"
            else:
                nuevo_nombre = f"{base_nombre}_{consecutivo:03d}{ext}"

            nuevo_archivo = archivo.with_name(nuevo_nombre)
            while nuevo_archivo.exists():
                consecutivo += 1
                nuevo_nombre = f"{base_nombre}_{consecutivo:03d}{ext}"
                nuevo_archivo = archivo.with_name(nuevo_nombre)
                contador_duplicados[base_nombre] = consecutivo

            archivo.rename(nuevo_archivo)
            writer.writerow([
                str(archivo),
                archivo.name,
                nuevo_nombre,
                fecha_str
            ])
            print(f"OK: {archivo.name} -> {nuevo_nombre}")
        except Exception as e:
            print(f"ERROR: {archivo.name} -> {e}")

print("\nProceso terminado. Revisar log_renombrado.csv")