"""Mueve una carpeta usando Robocopy en Windows."""

import argparse
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("origen", type=Path, nargs="?", help="carpeta que se va a mover")
    parser.add_argument("destino", type=Path, nargs="?", help="carpeta de destino")
    parser.add_argument("--ejecutar", action="store_true", help="confirma el movimiento real")
    args = parser.parse_args()
    modo_interactivo = args.origen is None or args.destino is None
    if args.origen is None:
        try:
            origen_texto = input("Ruta de origen: ").strip().strip('"')
        except EOFError:
            parser.error("indica una ruta de origen")
        if not origen_texto:
            parser.error("la ruta de origen no puede estar vacia")
        args.origen = Path(origen_texto)
    if args.destino is None:
        try:
            destino_texto = input("Ruta de destino: ").strip().strip('"')
        except EOFError:
            parser.error("indica una ruta de destino")
        if not destino_texto:
            parser.error("la ruta de destino no puede estar vacia")
        args.destino = Path(destino_texto)
    if not args.ejecutar:
        print(f"Simulacion: robocopy {args.origen} {args.destino} /MOVE /E /R:3 /W:1 /MT:32")
        if not modo_interactivo:
            print("Anade --ejecutar para realizar el movimiento.")
            return
        try:
            confirmacion = input("Ejecutar el movimiento? [s/N]: ").strip().lower()
        except EOFError:
            confirmacion = ""
        if confirmacion not in {"s", "si"}:
            print("Movimiento cancelado.")
            return
    resultado = subprocess.run(["robocopy", str(args.origen), str(args.destino), "/MOVE", "/E", "/R:3", "/W:1", "/MT:32"], check=False)
    if resultado.returncode >= 8:
        raise SystemExit(f"Robocopy termino con errores (codigo {resultado.returncode}).")


if __name__ == "__main__":
    main()