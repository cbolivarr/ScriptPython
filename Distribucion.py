import os
import shutil
import hashlib
import csv
from pathlib import Path

# =========================
# CONFIGURACION
# =========================

ORIGEN = r"C:\Users\camilo.bolivar_amari\Documents\Mis documentos\Fotos\Fotos"

TAMANO_LOTE_GB = 5

# =========================

MAX_BYTES = TAMANO_LOTE_GB * 1024 * 1024 * 1024

ARCHIVO_INVENTARIO = os.path.join(ORIGEN, "inventario_original.csv")
ARCHIVO_LOG = os.path.join(ORIGEN, "log_proceso.txt")

print("\n========== INICIANDO VALIDACIONES ==========\n")

# ---------------------------------
# Obtener archivos
# ---------------------------------

archivos = []

for root, dirs, files in os.walk(ORIGEN):

    dirs[:] = [d for d in dirs if not d.startswith("Lote_")]

    for archivo in files:

        ruta = os.path.join(root, archivo)

        try:
            tamano = os.path.getsize(ruta)

            archivos.append({
                "ruta": ruta,
                "nombre": archivo,
                "tamano": tamano
            })

        except Exception as e:
            print(f"ERROR: {ruta} -> {e}")

if not archivos:
    raise Exception("No se encontraron archivos")

# ---------------------------------
# Inventario
# ---------------------------------

print("Creando inventario...")

with open(ARCHIVO_INVENTARIO, "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)

    writer.writerow(["archivo", "tamano_bytes"])

    for item in archivos:
        writer.writerow([
            item["ruta"],
            item["tamano"]
        ])

total_bytes = sum(a["tamano"] for a in archivos)

print(
    f"Archivos encontrados: {len(archivos):,}"
)

print(
    f"Tamaño total: {total_bytes / (1024**3):.2f} GB"
)

# ---------------------------------
# Espacio disponible
# ---------------------------------

unidad = Path(ORIGEN).anchor

uso = shutil.disk_usage(unidad)

espacio_libre = uso.free

if espacio_libre < total_bytes:
    raise Exception(
        f"No hay espacio suficiente.\n"
        f"Libre: {espacio_libre/(1024**3):.2f} GB\n"
        f"Necesario: {total_bytes/(1024**3):.2f} GB"
    )

print(
    f"Espacio disponible: "
    f"{espacio_libre/(1024**3):.2f} GB"
)

# ---------------------------------
# HASH
# ---------------------------------

def sha256_archivo(ruta):

    h = hashlib.sha256()

    with open(ruta, "rb") as f:

        while chunk := f.read(1024 * 1024):
            h.update(chunk)

    return h.hexdigest()

# ---------------------------------
# Copia organizada
# ---------------------------------

print("\nOrganizando archivos...\n")

lote = 1
tamano_lote = 0

carpeta_lote = os.path.join(
    ORIGEN,
    f"Lote_{lote:03d}"
)

os.makedirs(carpeta_lote, exist_ok=True)

errores = []

for item in archivos:

    ruta = item["ruta"]
    nombre = item["nombre"]
    tamano = item["tamano"]

    if tamano_lote + tamano > MAX_BYTES:

        lote += 1
        tamano_lote = 0

        carpeta_lote = os.path.join(
            ORIGEN,
            f"Lote_{lote:03d}"
        )

        os.makedirs(carpeta_lote, exist_ok=True)

    destino = os.path.join(
        carpeta_lote,
        nombre
    )

    base, ext = os.path.splitext(nombre)

    contador = 1

    while os.path.exists(destino):

        destino = os.path.join(
            carpeta_lote,
            f"{base}_{contador}{ext}"
        )

        contador += 1

    try:

        print(f"Copiando {nombre}")

        shutil.copy2(
            ruta,
            destino
        )

        hash_origen = sha256_archivo(ruta)
        hash_destino = sha256_archivo(destino)

        if hash_origen != hash_destino:

            errores.append(
                f"HASH DIFERENTE: {ruta}"
            )

            os.remove(destino)

            continue

        tamano_lote += tamano

    except Exception as e:

        errores.append(
            f"{ruta} -> {str(e)}"
        )

# ---------------------------------
# Resumen
# ---------------------------------

with open(
    ARCHIVO_LOG,
    "w",
    encoding="utf-8"
) as log:

    if errores:

        log.write(
            "\n".join(errores)
        )

print("\n========================")
print("PROCESO FINALIZADO")
print("========================")
print(f"Lotes creados: {lote}")
print(f"Errores: {len(errores)}")
print(f"Inventario: {ARCHIVO_INVENTARIO}")
print(f"Log: {ARCHIVO_LOG}")

if errores:
    print(
        "\nRevise el archivo log antes de eliminar originales."
    )
else:
    print(
        "\nTodos los archivos fueron verificados correctamente."
    )
