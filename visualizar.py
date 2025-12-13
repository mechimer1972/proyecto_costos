import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import tempfile, os
from datetime import datetime
from base_datos import obtener_recetas
from base_datos import obtener_conformacion_receta


def visualizar_costos():
    ventana = tk.Toplevel()
    ventana.title("Visualizar Costos")
    ventana.state("zoomed")

    tk.Label(ventana, text="Visualización de Costos", font=("Arial", 20, "bold")).pack(pady=20)

    recetas = obtener_recetas()
    nombres_recetas = [r[1] for r in recetas]

    frame_seleccion = tk.LabelFrame(ventana, text="Seleccionar receta", font=("Arial", 12, "bold"), padx=10, pady=10)
    frame_seleccion.pack(pady=10)

    combo_recetas = ttk.Combobox(frame_seleccion, values=nombres_recetas, state="readonly", font=("Arial", 12), width=40)
    combo_recetas.pack(pady=10)

    frame_resultado = tk.LabelFrame(ventana, text="Datos de la receta", font=("Arial", 12, "bold"), padx=10, pady=10)
    frame_resultado.pack(pady=10, fill="x", padx=40)

    lbl_nombre = tk.Label(frame_resultado, text="Nombre: —", font=("Arial", 12))
    lbl_nombre.grid(row=0, column=0, padx=10, pady=5, sticky="w")

    lbl_rinde = tk.Label(frame_resultado, text="Rinde: — unidades", font=("Arial", 12))
    lbl_rinde.grid(row=1, column=0, padx=10, pady=5, sticky="w")

    lbl_costo_total = tk.Label(frame_resultado, text="Costo total de elaboración: $—", font=("Arial", 12))
    lbl_costo_total.grid(row=2, column=0, padx=10, pady=5, sticky="w")

    lbl_costo_unidad = tk.Label(frame_resultado, text="Costo por unidad: $—", font=("Arial", 12))
    lbl_costo_unidad.grid(row=3, column=0, padx=10, pady=5, sticky="w")


    frame_conformacion = tk.LabelFrame(ventana, text="Conformación de Receta", font=("Arial", 12, "bold"), padx=10, pady=10)
    frame_conformacion.pack(pady=10, fill="both", expand=True)

    tree_conformacion = ttk.Treeview(frame_conformacion, columns=("Materia", "Cantidad", "Costo"), show="headings", height=8)
    tree_conformacion.heading("Materia", text="Materia Prima")
    tree_conformacion.heading("Cantidad", text="Cantidad (g)")
    tree_conformacion.heading("Costo", text="Costo ($)")
    tree_conformacion.column("Materia", anchor="w", width=200)
    tree_conformacion.column("Cantidad", anchor="e", width=100)
    tree_conformacion.column("Costo", anchor="e", width=100)
    tree_conformacion.pack(fill="both", expand=True, padx=10, pady=10)


    def mostrar_datos(event=None):
        seleccion = combo_recetas.get()
        for r in recetas:
            if r[1] == seleccion:
                lbl_nombre.config(text=f"Nombre: {r[1]}")

                # —— VALORES CORRECTOS SIN CONVERSIONES ——
                rinde = float(r[7]) if r[7] else 0.0  # ya viene en unidades reales
                costo_total = float(r[5]) if r[5] else 0.0
                costo_unidad = float(r[9]) if r[9] else 0.0  # ya viene por unidad
                precio_envase = float(r[8]) if r[8] else 0.0
                costo_unidad_corr = (costo_total / rinde) + precio_envase

                lbl_rinde.config(text=f"Rinde: {rinde:.2f} unidades")
                lbl_costo_total.config(text=f"Costo total de elaboración: ${costo_total:.2f}")
                lbl_costo_unidad.config(text=f"Costo por unidad: ${costo_unidad:.2f}")
                lbl_costo_unidad.config(text=f"Costo por unidad: ${costo_unidad_corr:.2f}")

                # Ingredientes
                ingredientes = obtener_conformacion_receta(r[1])
                tree_conformacion.delete(*tree_conformacion.get_children())
                for nombre_mp, cantidad, costo in ingredientes:
                    tree_conformacion.insert("", "end", values=(nombre_mp, f"{cantidad:.2f}", f"${costo:.2f}"))
                break


    combo_recetas.bind("<<ComboboxSelected>>", mostrar_datos)



    # ---------------- IMPRESIÓN EN PANTALLA ---------------- #

    def imprimir_en_pantalla():
        recetas = obtener_recetas()
        if not recetas:
            messagebox.showinfo("Sin datos", "No hay recetas para mostrar.")
            return

        recetas_ordenadas = sorted(recetas, key=lambda r: r[1].lower())
        fecha_actual = datetime.now().strftime("%d/%m/%Y")

        encabezado = f"{'Listado de Costos de Recetas':^110}\n{'Fecha: ' + fecha_actual:^110}\n\n"
        columnas = f"{'Nombre Receta':<40}{'Costo Total':>20}{'Rinde':>15}{'Costo x Unidad':>20}\n"
        separador = "-" * 110 + "\n"

        filas = ""
        for r in recetas_ordenadas:
            nombre = r[1]
            costo_total = f"${r[5]:.2f}" if r[5] else "-"
            rinde = f"{r[7]:.2f}" if r[7] else "-"
            costo_unidad = f"${r[9]:.2f}" if r[9] else "-"

            filas += f"{nombre:<40}{costo_total:>20}{rinde:>15}{costo_unidad:>20}\n"

        texto = encabezado + columnas + separador + filas

        ventana_impresion = tk.Toplevel()
        ventana_impresion.title("Listado de Costos")

        ventana_impresion.attributes("-fullscreen", True)
        ventana_impresion.configure(bg="white")

        marco_central = tk.Frame(ventana_impresion, bg="white", padx=60, pady=40)
        marco_central.pack(expand=True)

        area_texto = tk.Text(
            marco_central,
            font=("Courier New", 13),
            bg="white",
            width=120,
            height=35
        )
        area_texto.insert(tk.END, texto)
        area_texto.config(state="disabled")
        area_texto.pack()

        btn_cerrar = tk.Button(
            marco_central,
            text="Cerrar pantalla completa",
            font=("Arial", 12, "bold"),
            command=ventana_impresion.destroy
        )
        btn_cerrar.pack(pady=20)



    # ---------------- IMPRESIÓN EN PAPEL ---------------- #

    def imprimir_en_papel():
        recetas = obtener_recetas()
        if not recetas:
            messagebox.showinfo("Sin datos", "No hay recetas para imprimir.")
            return

        confirmar = messagebox.askyesno("Confirmar impresión", "¿Estás segura/o de que querés imprimir el listado?")
        if not confirmar:
            return

        recetas_ordenadas = sorted(recetas, key=lambda r: r[1].lower())
        fecha_actual = datetime.now().strftime("%d/%m/%Y")

        ANCHO = 160

        encabezado = (
            f"{'Listado de Costos de Recetas':^{ANCHO}}\n"
            f"{('Fecha: ' + fecha_actual):^{ANCHO}}\n\n"
        )

        columnas = (
            f"{'Nombre de la Receta':<60}"
            f"{'Costo Total':>20}"
            f"{'Rinde':>15}"
            f"{'Costo por Unidad':>25}\n"
        )

        separador = "-" * ANCHO + "\n"

        filas = ""
        for r in recetas_ordenadas:
            nombre = r[1][:57] + "..." if len(r[1]) > 60 else r[1]
            costo_total = f"${r[5]:.2f}" if r[5] else "-"
            rinde = f"{r[7]:.2f}" if r[7] else "-"
            costo_unidad = f"${r[9]:.2f}" if r[9] else "-"

            filas += (
                f"{nombre:<60}"
                f"{costo_total:>20}"
                f"{rinde:>15}"
                f"{costo_unidad:>25}\n"
            )

        texto = encabezado + columnas + separador + filas

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as f:
            f.write(texto)
            ruta_archivo = f.name

        os.startfile(ruta_archivo)



    def mostrar_opciones_impresion():
        ventana_opciones = tk.Toplevel()
        ventana_opciones.title("Opciones de impresión")
        ventana_opciones.configure(bg="white")

        ancho, alto = 300, 150
        ventana_opciones.geometry(f"{ancho}x{alto}")

        ventana_opciones.update_idletasks()
        x = (ventana_opciones.winfo_screenwidth() // 2) - (ancho // 2)
        y = (ventana_opciones.winfo_screenheight() // 2) - (alto // 2)
        ventana_opciones.geometry(f"{ancho}x{alto}+{x}+{y}")

        lbl = tk.Label(ventana_opciones, text="¿Cómo querés imprimir?", font=("Arial", 12), bg="white")
        lbl.pack(pady=10)

        btn_pantalla = tk.Button(
            ventana_opciones,
            text="🖥️ Ver en pantalla",
            font=("Arial", 11),
            command=lambda:[ventana_opciones.destroy(), imprimir_en_pantalla()]
        )
        btn_pantalla.pack(pady=5)

        btn_papel = tk.Button(
            ventana_opciones,
            text="🖨️ Imprimir en papel",
            font=("Arial", 11),
            command=lambda:[ventana_opciones.destroy(), imprimir_en_papel()]
        )
        btn_papel.pack(pady=5)



    btn_imprimir = tk.Button(
        ventana,
        text="🖨️ Imprimir Costos",
        font=("Arial", 12, "bold"),
        bg="#e0e0e0",
        command=mostrar_opciones_impresion
    )
    btn_imprimir.pack(pady=10)

    btn_cerrar = tk.Button(
        ventana,
        text="Cerrar",
        font=("Arial", 12),
        width=20,
        command=ventana.destroy
    )
    btn_cerrar.pack(pady=20)
