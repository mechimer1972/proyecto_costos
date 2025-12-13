import tkinter as tk
from tkinter import ttk, messagebox
import tempfile
import os
from datetime import datetime
import sqlite3

from base_datos import (
    guardar_materia_prima,
    obtener_materias_primas,
    eliminar_materia,
    modificar_materia,
    obtener_precio_actual,
    registrar_modificacion,
    actualizar_costos_por_materia,
    RUTA_DB
)


def abrir_materias_primas():
    categorias_seleccionadas = []
    ventana = tk.Toplevel()
    ventana.title("ABM Materias Primas")
    ventana.state("zoomed")
    ventana.update_idletasks()

    # Contenedor para guardar el nombre original seleccionado (mutable para scope de funciones internas)
    original_nombre = [None]

    # Título centrado
    lbl_titulo = tk.Label(ventana, text="ABM de Materias Primas", font=("Arial", 20, "bold"))
    lbl_titulo.pack(pady=(20, 10))

    # --- Formulario de alta ---
    frame_form = tk.Frame(ventana)
    frame_form.pack(pady=10)

    tk.Label(frame_form, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
    entrada_nombre = tk.Entry(frame_form)
    entrada_nombre.grid(row=0, column=1, padx=5)

    tk.Label(frame_form, text="Categoría:").grid(row=1, column=0, padx=5, pady=5)
    categorias = [
        "Carnes", "Verduras", "Frutas", "Harináceos", "Huevos", "Lácteos",
        "Repostería", "Aceites", "Masas", "Salsas", "Rellenos", "Condimentos", "Panificados", "Fiambres", "Aditivos", "Frutos Secos", "Envases"
    ]
    combo_categoria = ttk.Combobox(frame_form, values=categorias, state="readonly")
    combo_categoria.grid(row=1, column=1, padx=5)

    tk.Label(frame_form, text="Precio por kg:").grid(row=2, column=0, padx=5, pady=5)
    entrada_precio = tk.Entry(frame_form)
    entrada_precio.grid(row=2, column=1, padx=5)

    tk.Label(frame_form, text="Proveedor:").grid(row=3, column=0, padx=5, pady=5)
    entrada_proveedor = tk.Entry(frame_form)
    entrada_proveedor.grid(row=3, column=1, padx=5)

    def seleccionar_categorias():
        ventana_cat = tk.Toplevel(ventana)
        ventana_cat.title("Seleccionar categorías")
        ventana_cat.geometry("300x400")
        ventana_cat.transient(ventana)
        ventana_cat.grab_set()

        seleccion_vars = {}
        todas_var = tk.BooleanVar()

        def confirmar_seleccion():
            categorias_seleccionadas.clear()
            if todas_var.get():
                categorias_seleccionadas.append("Todas")
            else:
                for cat, var in seleccion_vars.items():
                    if var.get():
                        categorias_seleccionadas.append(cat)
            ventana_cat.destroy()

        tk.Checkbutton(ventana_cat, text="Todas", variable=todas_var).pack(anchor="w", padx=10, pady=5)

        for cat in categorias:
            var = tk.BooleanVar()
            seleccion_vars[cat] = var
            tk.Checkbutton(ventana_cat, text=cat, variable=var).pack(anchor="w", padx=10)

        tk.Button(ventana_cat, text="Confirmar", command=confirmar_seleccion).pack(pady=15)

    def agregar():
        nombre = entrada_nombre.get().strip()
        categoria = combo_categoria.get().strip()
        proveedor = entrada_proveedor.get().strip()
        try:
            precio = float(entrada_precio.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Precio inválido", parent=ventana)
            return

        if not nombre or not categoria:
            messagebox.showerror("Error", "Faltan datos", parent=ventana)
            return

        # 🔹 Verificar si el nombre ya existe en la base de datos
        materias = obtener_materias_primas()
        nombres_existentes = [m[0].lower() for m in materias]  # compara en minúsculas
        if nombre.lower() in nombres_existentes:
            messagebox.showwarning(
                "Duplicado",
                f"Ya existe una materia prima con el nombre '{nombre}'.", parent=ventana
            )
            return

        # Si pasa la validación, se guarda normalmente (ahora con proveedor)
        ok = False
        try:
            guardar_materia_prima(nombre, categoria, precio, proveedor)
            ok = True
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la materia prima:\n{e}", parent=ventana)

        if ok:
            actualizar_lista()

            entrada_nombre.delete(0, tk.END)
            entrada_precio.delete(0, tk.END)
            combo_categoria.set("")
            entrada_proveedor.delete(0, tk.END)

            messagebox.showinfo("Éxito", f"'{nombre}' se agregó correctamente.", parent=ventana)

    tk.Button(frame_form, text="Agregar", command=agregar).grid(row=4, column=0, columnspan=2, pady=10)

    # --- Lista de productos ---
    frame_lista = tk.Frame(ventana)
    frame_lista.pack(pady=10)

    tree = ttk.Treeview(
        frame_lista,
        columns=("Nombre", "Categoría", "Precio", "Proveedor", "Fecha"),
        show="headings",
        height=20
    )
    tree.heading("Nombre", text="Materia Prima")
    tree.heading("Categoría", text="Categoría")
    tree.heading("Precio", text="Precio por Kg.")
    tree.heading("Proveedor", text="Proveedor")
    tree.heading("Fecha", text="Actualización")

    tree.column("Nombre", anchor="w", width=220)
    tree.column("Categoría", anchor="center", width=140)
    tree.column("Precio", anchor="e", width=110)
    tree.column("Proveedor", anchor="w", width=180)
    tree.column("Fecha", anchor="center", width=160)

    tree.pack(fill="both", expand=True, padx=20)

    def actualizar_lista():
        tree.delete(*tree.get_children())
        for nombre, categoria, precio, proveedor, fecha in obtener_materias_primas():
            tree.insert("", tk.END, values=(nombre, categoria, f"${precio:.2f}", proveedor or "", fecha))

    def eliminar():
        seleccion = tree.selection()
        if not seleccion:
            return

        valores = tree.item(seleccion[0])["values"]
        nombre_sel = valores[0]

        confirmar = messagebox.askyesno("Confirmar eliminación", f"¿Eliminar '{nombre_sel}' definitivamente?", parent=ventana)
        if confirmar:
            eliminar_materia(nombre_sel)
            tree.selection_remove(seleccion[0])
            actualizar_lista()

    def modificar():
        # Nombre original cargado al presionar "Cargar para modificar"
        nombre_original = original_nombre[0] if original_nombre[0] else entrada_nombre.get().strip()
        nombre_nuevo = entrada_nombre.get().strip()
        nueva_categoria = combo_categoria.get().strip()
        proveedor_texto = entrada_proveedor.get().strip()
        precio_texto = entrada_precio.get().strip().replace(",", ".").replace("$", "")

        if not nombre_nuevo or not nueva_categoria or not precio_texto:
            messagebox.showerror("Error", "Todos los campos son obligatorios", parent=ventana)
            return

        try:
            nuevo_precio = float(precio_texto)
        except ValueError:
            messagebox.showerror("Error", "Precio inválido. Usá solo números, con punto decimal si es necesario.")
            return

        # Obtener el precio actual antes de modificar (usamos nombre_original)
        precio_anterior = obtener_precio_actual(nombre_original)

        # Registrar la modificación en el historial SOLO si cambió el precio
        if precio_anterior != nuevo_precio:
            registrar_modificacion(nombre_original, precio_anterior, nuevo_precio)

        # Aplicar la modificación principal (no rompe la lógica de recalculo de recetas)
        try:
            # modificar_materia debe actualizar precio, categoria y proveedor para el registro identificado por nombre_original
            modificar_materia(nombre_original, nueva_categoria, nuevo_precio, proveedor_texto)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo modificar:\n{e}", parent=ventana)
            return

        # Si el nombre cambió, actualizamos el nombre en la tabla materias_primas Y en ingredientes_receta
        if nombre_nuevo and nombre_nuevo != nombre_original:
            try:
                conn = sqlite3.connect(RUTA_DB)
                cursor = conn.cursor()

                # Actualizar nombre en materias_primas
                cursor.execute("UPDATE materias_primas SET nombre = ? WHERE nombre = ?", (nombre_nuevo, nombre_original))

                # Actualizar referencia en ingredientes_receta (o la tabla que uses para ingredientes)
                cursor.execute("UPDATE ingredientes_receta SET materia = ? WHERE materia = ?", (nombre_nuevo, nombre_original))

                conn.commit()
                conn.close()

            except Exception as e:
                messagebox.showwarning("Advertencia", f"No se pudo renombrar totalmente la materia en todas las tablas:\n{e}", parent=ventana)

        # 🔄 Actualizar costos de recetas relacionadas (usar el nombre final)
        nombre_para_actualizar = nombre_nuevo if nombre_nuevo else nombre_original
        try:
            actualizar_costos_por_materia(nombre_para_actualizar)
        except Exception as e:
            # Si falla la actualización automática, avisar pero no interrumpir
            messagebox.showwarning("Advertencia", f"No se pudo actualizar costos de recetas automáticamente:\n{e}", parent=ventana)

        # (opcional) mostrar mensaje de confirmación
        messagebox.showinfo("Actualización", f"'{nombre_para_actualizar}' se actualizó correctamente y las recetas vinculadas se recalcularon (si fue posible).")

        # Reiniciar original_nombre y limpiar campos
        original_nombre[0] = None
        entrada_nombre.delete(0, tk.END)
        entrada_precio.delete(0, tk.END)
        combo_categoria.set("")
        entrada_proveedor.delete(0, tk.END)
        actualizar_lista()

    def imprimir():
        ventana_cat = tk.Toplevel(ventana)
        ventana_cat.title("Seleccionar categorías para imprimir")

        ancho = 400
        alto = 500
        x = ventana.winfo_screenwidth() // 2 - ancho // 2
        y = ventana.winfo_screenheight() // 2 - alto // 2
        ventana_cat.geometry(f"{ancho}x{alto}+{x}+{y}")
        ventana_cat.transient(ventana)
        ventana_cat.grab_set()

        seleccion_vars = {}
        todas_var = tk.BooleanVar()

        def confirmar_seleccion():
            seleccionadas = []
            if todas_var.get():
                seleccionadas.append("Todas")
            else:
                for cat, var in seleccion_vars.items():
                    if var.get():
                        seleccionadas.append(cat)

            ventana_cat.destroy()

            datos = obtener_materias_primas()
            if "Todas" in seleccionadas or not seleccionadas:
                filtrados = datos
            else:
                filtrados = [mp for mp in datos if mp[1] in seleccionadas]

            if not filtrados:
                messagebox.showinfo("Sin datos", "No hay materias primas para imprimir en esas categorías.")
                return

            confirmar = messagebox.askyesno("Confirmar impresión", f"¿Deseás imprimir {len(filtrados)} registros?")
            if not confirmar:
                return

            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as archivo:
                fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
                archivo.write(f"Listado de materias primas - Impreso el {fecha_actual}\n\n")
                archivo.write(f"{ 'Materia Prima':<25} { 'Categoría':<15} { 'Proveedor':<20} { 'Precio por Kg.':>15} { 'Actualización':>15}\n")
                archivo.write("-" * 100 + "\n")
                for nombre, categoria, precio, proveedor, fecha in filtrados:
                    fecha_sola = fecha.split(" ")[0]
                    archivo.write(f"{nombre:<25} {categoria:<15} { (proveedor or ''):<20} ${precio:>13.2f} {fecha_sola:>15}\n")
                archivo_path = archivo.name

            os.startfile(archivo_path, "print")

        tk.Checkbutton(ventana_cat, text="Todas", variable=todas_var).pack(anchor="w", padx=10, pady=5)
        for cat in categorias:
            var = tk.BooleanVar()
            seleccion_vars[cat] = var
            tk.Checkbutton(ventana_cat, text=cat, variable=var).pack(anchor="w", padx=10)

        tk.Button(ventana_cat, text="Confirmar selección", command=confirmar_seleccion).pack(pady=15)
    def cargar_para_modificar():
        seleccion = tree.selection()
        if not seleccion:
            return

        valores = tree.item(seleccion[0])["values"]
        entrada_nombre.delete(0, tk.END)
        entrada_nombre.insert(0, valores[0])
        combo_categoria.set(valores[1])
        # precio viene con $ en la lista
        entrada_precio.delete(0, tk.END)
        entrada_precio.insert(0, valores[2].replace("$", ""))
        entrada_proveedor.delete(0, tk.END)
        entrada_proveedor.insert(0, valores[3])

        # Guardar el nombre original para usar en la modificación
        original_nombre[0] = valores[0]

    # --- Botones alineados horizontalmente ---
    frame_botones = tk.Frame(ventana)
    frame_botones.pack(pady=15)

    btn_cargar = tk.Button(frame_botones, text="Cargar para modificar", width=20, command=cargar_para_modificar)
    btn_cargar.grid(row=0, column=0, padx=10)

    btn_modificar = tk.Button(frame_botones, text="Modificar", width=20, command=modificar)
    btn_modificar.grid(row=0, column=1, padx=10)

    btn_eliminar = tk.Button(frame_botones, text="Eliminar", width=20, command=eliminar)
    btn_eliminar.grid(row=0, column=2, padx=10)

    btn_imprimir = tk.Button(frame_botones, text="Imprimir por categoría", width=20, command=imprimir)
    btn_imprimir.grid(row=0, column=3, padx=10)

    actualizar_lista()
    # --- Botón Cerrar centrado al final ---
    frame_cerrar = tk.Frame(ventana)
    frame_cerrar.pack(pady=20)

    btn_cerrar = tk.Button(frame_cerrar, text="Cerrar", width=20, command=ventana.destroy)
    btn_cerrar.pack()

