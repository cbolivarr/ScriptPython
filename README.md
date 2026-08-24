# ScriptPython

Coleccion de utilidades personales para organizar archivos y calcular expresiones en Windows.

## Estructura

```text
src/script_python/
  calculadora.py       # Interfaz Flet y evaluador aritmetico seguro
  distribucion.py      # Copia verificada en lotes
  mover_archivos.py    # Movimiento con Robocopy
  renombrar.py         # Renombrado de imagenes y videos por fecha
```

## Instalacion

Se recomienda Python 3.10 o superior y un entorno virtual:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
```

## Uso

```powershell
calculadora
renombrar-medios "C:\Ruta\Fotos"                 # simulacion
renombrar-medios "C:\Ruta\Fotos" --aplicar
distribuir-archivos "C:\Ruta\Fotos" --tamano-lote-gb 5
mover-archivos "C:\Origen" "C:\Destino"         # simulacion
mover-archivos "C:\Origen" "C:\Destino" --ejecutar
```

El renombrador genera un CSV y no cambia nombres salvo que se indique `--aplicar`. El movimiento usa Robocopy y requiere Windows. Las operaciones de distribucion crean `Lote_NNN`, `inventario_original.csv` y `log_proceso.txt` dentro del origen.

## Desarrollo

Para ejecutar un modulo sin instalar el paquete:

```powershell
python -m script_python.renombrar "C:\Ruta\Fotos"
```

Antes de publicar cambios, comprueba la sintaxis con `python -m compileall src`.
