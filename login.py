import os
import sys

# Detecta la carpeta base correctamente incluso dentro del exe
BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))

RUTA_USUARIOS = os.path.join(BASE_DIR, "usuarios.txt")

def verificar_usuario(usuario, contraseña):
    try:
        with open(RUTA_USUARIOS, "r") as archivo:
            for linea in archivo:
                u, c = linea.strip().split(",")
                if u == usuario and c == contraseña:
                    return True
    except FileNotFoundError:
        print("Archivo de usuarios no encontrado")
    return False

def registrar_usuario(usuario, contraseña):
    with open(RUTA_USUARIOS, "a") as archivo:
        archivo.write(f"{usuario},{contraseña}\n")
