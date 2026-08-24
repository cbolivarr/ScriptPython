"""Renombra imagenes y videos usando fecha EXIF o fecha de modificacion."""

import argparse
import csv
import os
from datetime import datetime
from pathlib import Path

from PIL import ExifTags, Image
import pillow_heif


IMAGENES = {".jpg", ".jpeg", ".heic", ".png"}
VIDEOS = {".mp4", ".mov"}


def obtener_fecha_exif(ruta: Path):
    try:
        with Image.open(ruta) as imagen:
            for tag_id, valor in imagen.getexif().items():
                if ExifTags.TAGS.get(tag_id) in {"DateTimeOriginal", "DateTimeDigitized", "DateTime"}:
                    if isinstance(valor, bytes):
                        valor = valor.decode(errors="ignore")
                    return datetime.strptime(valor, "%Y:%m:%d %H:%M:%S")
    except (OSError, ValueError, UnicodeError):
        return None
    return None


def ejecutar(ruta: Path, aplicar: bool, log_path: Path) -> int:
    pillow_heif.register_heif_opener()
    contador = {}
    archivos = sorted(p for p in ruta.rglob("*") if p.is_file() and p.suffix.lower() in IMAGENES | VIDEOS)
    with log_path.open("w", newline="", encoding="utf-8") as log:
        writer = csv.writer(log)
        writer.writerow(["ruta_original", "nombre_original", "nombre_nuevo", "fecha_utilizada"])
        for archivo in archivos:
            fecha = obtener_fecha_exif(archivo) if archivo.suffix.lower() in {".jpg", ".jpeg", ".heic"} else None
            fecha = fecha or datetime.fromtimestamp(os.path.getmtime(archivo))
            base = f"{'IMG' if archivo.suffix.lower() in IMAGENES else 'VID'}_{fecha:%Y%m%d_%H%M%S}"
            contador[base] = contador.get(base, 0) + 1
            indice = contador[base]
            nuevo = archivo.with_name(f"{base}{archivo.suffix.lower()}" if indice == 1 else f"{base}_{indice:03d}{archivo.suffix.lower()}")
            while nuevo.exists() and nuevo != archivo:
                indice += 1
                nuevo = archivo.with_name(f"{base}_{indice:03d}{archivo.suffix.lower()}")
            writer.writerow([archivo, archivo.name, nuevo.name, fecha.isoformat(sep=" ")])
            print(f"{'OK' if aplicar else 'SIMULACION'}: {archivo.name} -> {nuevo.name}")
            if aplicar and nuevo != archivo:
                archivo.rename(nuevo)
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ruta", type=Path, nargs="?", help="carpeta con imagenes y videos")
    parser.add_argument("--aplicar", action="store_true", help="ejecuta los cambios; por defecto solo simula")
    parser.add_argument("--log", type=Path, default=Path("log_renombrado.csv"))
    args = parser.parse_args()
    if args.ruta is None:
        try:
            ruta_texto = input("Ruta de la carpeta: ").strip().strip('"')
        except EOFError:
            parser.error("indica una carpeta para renombrar")
        if not ruta_texto:
            parser.error("la carpeta no puede estar vacia")
        args.ruta = Path(ruta_texto)
    if not args.aplicar:
        print("Modo simulacion: no se cambiaran nombres.")
        try:
            confirmacion = input("Aplicar renombrado? [s/N]: ").strip().lower()
        except EOFError:
            confirmacion = ""
        if confirmacion in {"s", "si"}:
            args.aplicar = True
    raise SystemExit(ejecutar(args.ruta, args.aplicar, args.log))


if __name__ == "__main__":
    main()