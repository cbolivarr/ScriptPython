import subprocess

origen = r"C:\Users\Usuario\Pictures\Pictures"
destino = r"C:\Users\Usuario\Documents"

subprocess.run(
    [
        "robocopy",
        origen,
        destino,
        "/MOVE",
        "/E",
        "/R:3",
        "/W:1",
        "/MT:32"
    ],
    check=False
)

print("Proceso finalizado.")
