import subprocess

origen = r"C:\Users\camilo.bolivar_amari\Documents\Mis documentos\Fotos\Fotos"
destino = r"C:\Users\camilo.bolivar_amari\Documents\Mis documentos"

subprocess.run([
    "robocopy",
    origen,
    destino,
    "/MOVE",
    "/E",
    "/R:3",
    "/W:1"
])