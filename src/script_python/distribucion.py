"""Copia archivos en lotes con inventario y verificacion SHA-256."""

import argparse
import csv
import hashlib
import shutil
from pathlib import Path


def sha256_archivo(ruta: Path) -> str:
    digest = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            digest.update(bloque)
    return digest.hexdigest()


def ejecutar(origen: Path, tamano_lote_gb: float) -> int:
    """Organiza archivos sin volver a leer carpetas Lote_NNN."""
    if not origen.is_dir():
        raise NotADirectoryError(f"No existe la carpeta: {origen}")
    archivos = [p for p in origen.rglob("*") if p.is_file() and not any(parte.startswith("Lote_") for parte in p.relative_to(origen).parts)]
    if not archivos:
        raise FileNotFoundError("No se encontraron archivos")

    inventario = origen / "inventario_original.csv"
    with inventario.open("w", newline="", encoding="utf-8") as salida:
        writer = csv.writer(salida)
        writer.writerow(["archivo", "tamano_bytes"])
        for archivo in archivos:
            writer.writerow([archivo, archivo.stat().st_size])

    total = sum(archivo.stat().st_size for archivo in archivos)
    if shutil.disk_usage(origen.anchor).free < total:
        raise OSError("No hay espacio suficiente para completar la copia")

    max_bytes = int(tamano_lote_gb * 1024**3)
    errores = []
    lote, acumulado = 1, 0
    print(f"Destino de las copias: {origen / 'Lote_NNN'}")
    for archivo in archivos:
        tamano = archivo.stat().st_size
        if acumulado and acumulado + tamano > max_bytes:
            lote, acumulado = lote + 1, 0
        carpeta = origen / f"Lote_{lote:03d}"
        carpeta.mkdir(exist_ok=True)
        destino = carpeta / archivo.name
        contador = 1
        while destino.exists():
            destino = carpeta / f"{archivo.stem}_{contador}{archivo.suffix}"
            contador += 1
        try:
            print(f"Copiando {archivo.name}")
            shutil.copy2(archivo, destino)
            if sha256_archivo(archivo) != sha256_archivo(destino):
                destino.unlink(missing_ok=True)
                raise OSError("hash SHA-256 diferente")
            acumulado += tamano
        except OSError as error:
            errores.append(f"{archivo} -> {error}")

    (origen / "log_proceso.txt").write_text("\n".join(errores), encoding="utf-8")
    print(f"Proceso finalizado: {len(archivos) - len(errores)} copiados, {len(errores)} errores")
    print(f"Revisa las carpetas Lote_001, Lote_002, etc. dentro de: {origen}")
    return 1 if errores else 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("origen", type=Path, nargs="?", help="carpeta que se va a distribuir")
    parser.add_argument("--tamano-lote-gb", type=float, default=5)
    args = parser.parse_args()
    if args.origen is None:
        try:
            ruta_texto = input("Ruta de la carpeta de origen: ").strip().strip('"')
        except EOFError:
            parser.error("indica una carpeta de origen como argumento")
        if not ruta_texto:
            parser.error("la carpeta de origen no puede estar vacia")
        args.origen = Path(ruta_texto)
    raise SystemExit(ejecutar(args.origen, args.tamano_lote_gb))


if __name__ == "__main__":
    main()