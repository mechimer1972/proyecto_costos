from datetime import datetime
import shutil
import os

def obtener_fecha_hora_actual():
    ahora = datetime.now()
    return ahora.strftime("%A %d/%m/%Y %H:%M")

def centrar_ventana(ventana):
    ventana.update_idletasks()
    ancho = ventana.winfo_width()
    alto = ventana.winfo_height()
    x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
    y = (ventana.winfo_screenheight() // 2) - (alto // 2)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

def crear_backup():
    # Crear carpeta backups si no existe
    if not os.path.exists("backups"):
        os.makedirs("backups")

    fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    origen = "bd_costos.db"
    destino = f"backups/bd_costos_backup_{fecha}.db"

    try:
        shutil.copy(origen, destino)
        return True, destino
    except Exception as e:
        return False, str(e)  

