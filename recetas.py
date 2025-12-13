import tkinter as tk
from tkinter import ttk, messagebox
from base_datos import obtener_materias_primas, obtener_precio_actual, agregar_receta, modificar_receta, obtener_recetas, obtener_conformacion_receta

def abrir_recetas():
    ventana = tk.Toplevel()
    ventana.title("Gestión de Recetas")
    ventana.state("zoomed")

    # Variables globales usadas por las funciones internas
    global entrada_nombre, entrada_merma, entrada_peso_unidad, combo_envase, ingredientes
    global tabla
    global lbl_peso, lbl_costo, lbl_peso_final, lbl_rinde, lbl_costo_unidad
    ingredientes = []

    global frame_ingredientes, combo_mp, entrada_cantidad
    global btn_agregar, btn_modificar, btn_eliminar, lista_ingredientes

    frame_ingredientes = None
    combo_mp = None
    entrada_cantidad = None
    btn_agregar = None
    btn_modificar = None
    btn_eliminar = None
    lista_ingredientes = None

    # =============================
    # ENCABEZADO
    # =============================
    frame_titulo = tk.Frame(ventana)
    frame_titulo.pack(pady=10)
    lbl_titulo = tk.Label(frame_titulo, text="ABM de Recetas", font=("Arial", 20, "bold"))
    lbl_titulo.pack()

    # =============================
    # BUSCADOR DE RECETAS (Combobox)
    # =============================
    frame_buscar = tk.Frame(ventana)
    frame_buscar.pack(pady=10)
    tk.Label(frame_buscar, text="Buscar receta:", font=("Arial", 12)).grid(row=0, column=0, padx=5)
    
    recetas = obtener_recetas()
    nombres_recetas = [r[1] for r in recetas]
    combo_recetas = ttk.Combobox(frame_buscar, values=nombres_recetas, state="readonly", font=("Arial", 12), width=40)
    combo_recetas.grid(row=0, column=1, padx=5)

    tk.Button(frame_buscar, text="Cargar receta", command=lambda: cargar_receta_seleccionada()).grid(row=0, column=2, padx=5)

    # =============================
    # NOMBRE DE LA RECETA
    # =============================
    frame_nombre = tk.Frame(ventana)
    frame_nombre.pack(pady=10)
    tk.Label(frame_nombre, text="Nombre de la receta:", font=("Arial", 12)).grid(row=0, column=0, padx=5)
    entrada_nombre = tk.Entry(frame_nombre, font=("Arial", 12), width=50)
    entrada_nombre.grid(row=0, column=1, padx=5)

    # ... (el resto de tu código sigue igual, sin mover nada)

    # =============================
    # INGREDIENTES (cantidad en KG)
    # =============================
    frame_ingredientes = tk.LabelFrame(ventana, text="Ingredientes", font=("Arial", 12, "bold"), padx=10, pady=10)
    frame_ingredientes.pack(pady=10, fill="x", padx=20)

    tk.Label(frame_ingredientes, text="Materia prima:", font=("Arial", 11)).grid(row=0, column=0, padx=5, pady=5)
    materias_primas = [mp[0] for mp in obtener_materias_primas()]
    combo_mp = ttk.Combobox(frame_ingredientes, values=materias_primas, width=30, state="readonly")
    combo_mp.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_ingredientes, text="Cantidad (kg):", font=("Arial", 11)).grid(row=0, column=2, padx=5, pady=5)
    entrada_cantidad = tk.Entry(frame_ingredientes, width=12)
    entrada_cantidad.grid(row=0, column=3, padx=5, pady=5)

    btn_agregar = tk.Button(frame_ingredientes, text="Agregar ingrediente", command=lambda: agregar_ingrediente())
    btn_agregar.grid(row=0, column=4, padx=10, pady=5)

    btn_modificar = tk.Button(frame_ingredientes, text="Modificar ingrediente", command=lambda: [modificar_ingrediente(), actualizar_totales()])
    btn_modificar.grid(row=0, column=5, padx=10, pady=5)

    btn_eliminar = tk.Button(frame_ingredientes, text="Eliminar ingrediente", command=lambda: [eliminar_ingrediente(), actualizar_totales()])
    btn_eliminar.grid(row=0, column=6, padx=10, pady=5)

    

    # =============================
    # TABLA (Cantidad en KG)
    # =============================
    frame_tabla = tk.Frame(ventana)
    frame_tabla.pack(pady=10, fill="both", expand=True)
    tabla = ttk.Treeview(frame_tabla, columns=("Materia", "Cantidad", "Costo"), show="headings", height=12)
    tabla.heading("Materia", text="Materia Prima")
    tabla.heading("Cantidad", text="Cantidad (kg)")
    tabla.heading("Costo", text="Costo ($)")
    tabla.column("Materia", width=300)
    tabla.column("Cantidad", width=120, anchor="center")
    tabla.column("Costo", width=120, anchor="e")
    tabla.pack(fill="both", expand=True)

    # =============================
    # TOTALES
    # =============================
    frame_totales = tk.LabelFrame(ventana, text="Totales de la receta", font=("Arial", 12, "bold"), padx=10, pady=10)
    frame_totales.pack(pady=10, fill="x", padx=20)

    lbl_peso = tk.Label(frame_totales, text="Peso total: 0.0000 kg", font=("Arial", 11))
    lbl_peso.grid(row=0, column=0, padx=10)

    tk.Label(frame_totales, text="Merma (%):", font=("Arial", 11)).grid(row=0, column=1, padx=5)
    entrada_merma = tk.Entry(frame_totales, width=6)
    entrada_merma.grid(row=0, column=2, padx=5)
    entrada_merma.bind("<KeyRelease>", lambda e: actualizar_totales())

    lbl_peso_final = tk.Label(frame_totales, text="Peso final: 0.0000 kg", font=("Arial", 11))
    lbl_peso_final.grid(row=0, column=3, padx=10)

    lbl_costo = tk.Label(frame_totales, text="Costo total: $0.00", font=("Arial", 11, "bold"))
    lbl_costo.grid(row=0, column=4, padx=10)

    # =============================
    # UNIDAD Y ENVASE
    # =============================
    frame_unidad = tk.LabelFrame(ventana, text="Unidad de producto final", font=("Arial", 12, "bold"), padx=10, pady=10)
    frame_unidad.pack(pady=10, fill="x", padx=20)

    tk.Label(frame_unidad, text="Peso por unidad (Kg):", font=("Arial", 11)).grid(row=0, column=0, padx=5, pady=5)
    entrada_peso_unidad = tk.Entry(frame_unidad, width=10)
    entrada_peso_unidad.grid(row=0, column=1, padx=5, pady=5)

    envases = [mp[0] for mp in obtener_materias_primas() if mp[1].strip().lower() == "envases"]
    tk.Label(frame_unidad, text="Envases:", font=("Arial", 11)).grid(row=0, column=2, padx=5, pady=5)
    combo_envase = ttk.Combobox(frame_unidad, values=envases, width=30, state="readonly")
    combo_envase.grid(row=0, column=3, padx=5, pady=5)

    lbl_rinde = tk.Label(frame_unidad, text="Rinde: — Unidades", font=("Arial", 11))
    lbl_rinde.grid(row=0, column=4, padx=20)
    lbl_costo_unidad = tk.Label(frame_unidad, text="Costo por unidad: —", font=("Arial", 11, "bold"))
    lbl_costo_unidad.grid(row=0, column=5, padx=20)

    # =============================
    # FUNCIONES INTERNAS
    # =============================
    def agregar_ingrediente():
        nombre = combo_mp.get().strip()
        if not nombre:
            messagebox.showerror("Error", "Seleccioná una materia prima.", parent=ventana)
            return

        try:
            cantidad = float(entrada_cantidad.get().strip()) if entrada_cantidad.get().strip() else 0.0
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Cantidad inválida. Ingresá un número (ej. 0.5 para medio kg).", parent=ventana)
            return

        precio_unitario = float(obtener_precio_actual(nombre))
        costo = round(precio_unitario * cantidad, 2)

        # Guardar ingrediente
        ingredientes.append((nombre, float(cantidad), float(costo)))

        # Ordenar por nombre
        ingredientes.sort(key=lambda x: x[0])

        # Refrescar tabla completa
        for item in tabla.get_children():
            tabla.delete(item)

        for ing in ingredientes:
            tabla.insert("", "end", values=(ing[0], f"{ing[1]:.4f}", f"${ing[2]:.2f}"))

        actualizar_totales()


        # Resetear campos
        combo_mp.set("")
        entrada_cantidad.delete(0, tk.END)
        combo_mp.focus_set()

    def modificar_ingrediente():
        seleccionado = tabla.selection()
        if not seleccionado:
            messagebox.showerror("Error", "Seleccioná un ingrediente para modificar.", parent=ventana)
            return

        item_id = seleccionado[0]
        idx = tabla.index(item_id)

        # Validar nueva cantidad
        try:
            nueva_cantidad = float(entrada_cantidad.get().strip())
            if nueva_cantidad <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Cantidad inválida.", parent=ventana)
            return

        nuevo_nombre = combo_mp.get().strip()
        if not nuevo_nombre:
            messagebox.showerror("Error", "Seleccioná una materia prima.", parent=ventana)
            return

        # Calcular nuevo costo
        precio_unitario = obtener_precio_actual(nuevo_nombre)
        nuevo_costo = round(precio_unitario * nueva_cantidad, 2)

        # Actualizar lista interna
        if 0 <= idx < len(ingredientes):
            ingredientes[idx] = (nuevo_nombre, nueva_cantidad, nuevo_costo)

        # Actualizar visualmente el Treeview
        tabla.item(item_id, values=(nuevo_nombre, f"{nueva_cantidad:.4f}", f"${nuevo_costo:.2f}"))

        # Recalcular totales
        actualizar_totales()

        # Limpiar campos
        combo_mp.set("")
        entrada_cantidad.delete(0, tk.END)
        combo_mp.focus_set()

    def eliminar_ingrediente():
        seleccion = tabla.selection()
        if not seleccion:
            messagebox.showerror("Error", "Seleccioná un ingrediente para eliminar.", parent=ventana)
            return
        idx = tabla.index(seleccion[0])
        tabla.delete(seleccion[0])
        if 0 <= idx < len(ingredientes):
            ingredientes.pop(idx)
        actualizar_totales()

    def actualizar_totales():
        """Recalcula peso total, merma y peso final en gramos"""
        try:
            if not ingredientes:
                lbl_peso.config(text="Peso total: 0.00 Kg")
                lbl_peso_final.config(text="Peso final: 0.00 Kg")
                lbl_costo.config(text="Costo total: $0.00")
                return

            # --- Cálculo del peso total y costo total ---
            peso_total_gramos = sum(i[1] for i in ingredientes)
            costo_total = sum(i[2] for i in ingredientes)

            lbl_peso.config(text=f"Peso total: {peso_total_gramos:.4f} g")
            lbl_costo.config(text=f"Costo total: ${costo_total:.2f}")

            # --- Calcular peso final considerando la merma ---
            try:
                merma = float(entrada_merma.get().strip()) if entrada_merma.get().strip() else 0
            except ValueError:
                merma = 0

            peso_final_gramos = peso_total_gramos * (1 - merma / 100)
            lbl_peso_final.config(text=f"Peso final: {peso_final_gramos:.4f} g")

            # --- Actualizar rinde y costo por unidad ---
            actualizar_rinde_y_costo()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar los totales: {e}")

    def actualizar_rinde_y_costo():
        # definir variables por defecto para evitar errores
        peso_total_kg = 0.0
        peso_final_kg = 0.0

        try:
            peso_unidad_g = float(entrada_peso_unidad.get().strip()) if entrada_peso_unidad.get().strip() else 0.0
            peso_unidad_kg = peso_unidad_g / 1000.0

            if peso_unidad_kg <= 0:
                lbl_rinde.config(text="Rinde: — unidades")
                lbl_costo_unidad.config(text="Costo por unidad: —")
                return

            # ahora las reasigna
            peso_total_kg = sum(float(i[1]) for i in ingredientes)
            merma = float(entrada_merma.get().strip()) if entrada_merma.get().strip() else 0.0
            costo_total = sum(float(i[2]) for i in ingredientes)

            peso_final_kg = peso_total_kg * (1 - merma / 100.0)

            lbl_peso.config(text=f"Peso total: {peso_total_kg:.2f} kg")
            lbl_peso_final.config(text=f"Peso final: {peso_final_kg:.2f} kg")

            rinde = peso_final_kg / peso_unidad_kg if peso_unidad_kg > 0 else 0.0
            costo_unitario = (costo_total) / rinde if rinde > 0 else 0.0

            lbl_rinde.config(text=f"Rinde: {rinde:.2f} unidades")
            lbl_costo_unidad.config(text=f"Costo por unidad: ${costo_unitario:.2f}")

        except Exception as e:
            print("Error en actualizar_rinde_y_costo:", e)
            lbl_rinde.config(text="Rinde: — unidades")
            lbl_costo_unidad.config(text="Costo por unidad: —")

    def eliminar_receta():
        nombre_receta = combo_recetas.get().strip()
        if not nombre_receta:
            messagebox.showerror("Error", "Seleccioná una receta para eliminar.", parent=ventana)
            return

        # Confirmación antes de borrar
        confirm = messagebox.askyesno("Confirmar eliminación", 
                                    f"¿Seguro que querés eliminar la receta '{nombre_receta}'?",
                                    parent=ventana)
        if not confirm:
            return

        try:
            # Buscar la receta en la lista cargada
            receta = next((r for r in recetas if r[1] == nombre_receta), None)
            if not receta:
                messagebox.showerror("Error", f"No se encontró la receta '{nombre_receta}' en la base.", parent=ventana)
                return

            # Eliminar usando la función de bd
            from base_datos import eliminar_receta
            eliminar_receta(receta[0])  # receta[0] es el ID

            messagebox.showinfo("Receta eliminada", f"La receta '{nombre_receta}' fue eliminada correctamente.", parent=ventana)

            # ==========================================
            # 🔄 ACTUALIZAR LISTA DE RECETAS Y COMBOBOX
            # ==========================================
            from base_datos import obtener_recetas
            nuevas_recetas = obtener_recetas()

            recetas.clear()
            recetas.extend(nuevas_recetas)

            combo_recetas["values"] = [r[1] for r in nuevas_recetas]
            combo_recetas.set("")  # limpia selección

            # También limpiar la vista o labels si querés:
            # limpiar_campos()

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un problema al eliminar la receta: {e}", parent=ventana)

            # Limpiar campos y refrescar lista
            limpiar()
            combo_recetas['values'] = [r[1] for r in obtener_recetas()]
            combo_recetas.set("")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar la receta:\n{e}", parent=ventana)
    
    # =============================
    # GUARDAR Y LIMPIAR
    # =============================
    def guardar_receta():
        nombre = entrada_nombre.get().strip()
        if not nombre:
            messagebox.showerror("Error", "Ingresá el nombre de la receta.", parent=ventana)
            return

        if not ingredientes:
            messagebox.showerror("Error", "La receta no tiene ingredientes.", parent=ventana)
            return

       # --- CÁLCULOS BASE ---
        peso_total_kg = sum(float(i[1]) for i in ingredientes)
        costo_total = sum(float(i[2]) for i in ingredientes)

        # Merma (%)
        merma = float(entrada_merma.get().strip()) if entrada_merma.get().strip() else 0.0
        peso_final_kg = peso_total_kg * (1 - merma / 100.0)

        # Peso por unidad (g → kg)
        peso_unidad_g = float(entrada_peso_unidad.get().strip()) if entrada_peso_unidad.get().strip() else 0.0
        peso_unidad_kg = peso_unidad_g / 1000.0 if peso_unidad_g > 0 else 0.0

        # Envase
        envase = combo_envase.get().strip()

        # Precio del envase
        precio_env = obtener_precio_actual(envase)
        try:
            costo_envase = float(precio_env) if precio_env is not None else 0.0
        except:
            costo_envase = 0.0

        print("DEBUG → Envase:", envase, "| Precio:", costo_envase)

        # ---- CÁLCULO CORRECTO ----

        # Rinde en unidades reales
        rinde = peso_final_kg / peso_unidad_kg if peso_unidad_kg > 0 else 0.0

        # Costo por unidad correcto
        costo_unidad = (costo_total / rinde) + costo_envase if rinde > 0 else 0.0

        # --- GUARDADO ---
        try:
            agregar_receta(
                nombre,
                ingredientes,              # Lista original de ingredientes
                float(peso_total_kg),
                float(merma),
                float(peso_final_kg),
                float(costo_total),
                float(peso_unidad_g),     # se guarda en kg
                float(rinde),
                float(costo_envase),
                float(costo_unidad)
                # Si querés guardar costo_envase: float(costo_envase)
            )

            messagebox.showinfo(
                "Receta guardada",
                f"La receta '{nombre}' fue guardada correctamente.",
                parent=ventana
            )

            limpiar()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la receta: {e}", parent=ventana)

    def limpiar():
        entrada_nombre.delete(0, tk.END)
        entrada_merma.delete(0, tk.END)
        entrada_peso_unidad.delete(0, tk.END)
        combo_envase.set("")
        tabla.delete(*tabla.get_children())
        ingredientes.clear()

        lbl_peso.config(text="Peso total: — kg")
        lbl_peso_final.config(text="Peso final: — kg")
        lbl_costo.config(text="Costo total: $0.00")
        lbl_rinde.config(text="Rinde: — unidades")
        lbl_costo_unidad.config(text="Costo por unidad: —")

        entrada_nombre.focus_set()


    # =============================
    # EVENTOS Y BOTONES
    # =============================
    entrada_merma.bind("<KeyRelease>", lambda e: actualizar_totales())
    entrada_peso_unidad.bind("<KeyRelease>", lambda e: actualizar_totales())
    combo_envase.bind("<<ComboboxSelected>>", lambda e: actualizar_totales())

    frame_botonera = tk.Frame(ventana)
    frame_botonera.pack(pady=20)

    tk.Button(frame_botonera, text="Eliminar receta", width=20, command=eliminar_receta).grid(row=0, column=0, padx=10)
    tk.Button(frame_botonera, text="Guardar receta", width=20, command=guardar_receta).grid(row=0, column=1, padx=10)
    tk.Button(frame_botonera, text="Limpiar campos", width=20, command=limpiar).grid(row=0, column=2, padx=10)
    tk.Button(frame_botonera, text="Cerrar", width=20, command=ventana.destroy).grid(row=0, column=3, padx=10)
    tk.Button(frame_botonera, text="✏️ Modificar receta", width=20, command=lambda: abrir_modificacion()).grid(row=0, column=4, padx=10)

    # Inicializamos totales
    actualizar_totales()

    # =============================
    # MODIFICAR Y CARGAR RECETAS
    # =============================
    def abrir_modificacion():
        seleccion = combo_recetas.get()
        if not seleccion:
            messagebox.showerror("Error", "Seleccioná una receta para modificar.", parent=ventana)
            return

        for r in recetas:
            if r[1] == seleccion:
                ventana_modificar = tk.Toplevel()
                ventana_modificar.title(f"Modificar receta: {r[1]}")
                ventana_modificar.geometry("600x500")

                tk.Label(ventana_modificar, text="Nombre:").pack()
                entrada_nombre_mod = tk.Entry(ventana_modificar)
                entrada_nombre_mod.pack()
                entrada_nombre_mod.insert(0, r[1])

                tk.Label(ventana_modificar, text="Merma (%):").pack()
                entrada_merma_mod = tk.Entry(ventana_modificar)
                entrada_merma_mod.pack()
                entrada_merma_mod.insert(0, r[3] if r[3] is not None else "")

                tk.Label(ventana_modificar, text="Peso por unidad (g):").pack()
                entrada_peso_unidad_mod = tk.Entry(ventana_modificar)
                entrada_peso_unidad_mod.pack()
                entrada_peso_unidad_mod.insert(0, r[6] if r[6] is not None else "")

                tk.Label(ventana_modificar, text="Envase:").pack()
                entrada_envase_mod = tk.Entry(ventana_modificar)
                entrada_envase_mod.pack()
                entrada_envase_mod.insert(0, r[8] if r[8] is not None else "")

                def guardar_cambios():
                    nuevos_datos = {
                        "nombre": entrada_nombre_mod.get(),
                        "merma": float(entrada_merma_mod.get() or 0),
                        "peso_unidad": float(entrada_peso_unidad_mod.get() or 0),
                        "envase": entrada_envase_mod.get()
                    }
                    modificar_receta(r[0], nuevos_datos)
                    messagebox.showinfo("Modificado", "La receta fue actualizada correctamente.", parent=ventana_modificar)
                    ventana_modificar.destroy()

                tk.Button(ventana_modificar, text="Guardar cambios", command=guardar_cambios).pack(pady=20)
                break

    def cargar_receta_seleccionada(event=None):
        nombre_receta = combo_recetas.get().strip()
        if not nombre_receta:
            return

        receta = next((r for r in recetas if r[1] == nombre_receta), None)
        if not receta:
            messagebox.showerror("Error", f"No se encontró la receta '{nombre_receta}' en la base.", parent=ventana)
            return

        # Cargar campos generales
        entrada_nombre.delete(0, tk.END)
        entrada_nombre.insert(0, receta[1])

        entrada_merma.delete(0, tk.END)
        entrada_merma.insert(0, receta[3] if receta[3] is not None else "")

        entrada_peso_unidad.delete(0, tk.END)
        entrada_peso_unidad.insert(0, receta[6] if receta[6] is not None else "")

        combo_envase.set(receta[8] if receta[8] else "")

        # Limpiar tabla y lista interna
        tabla.delete(*tabla.get_children())
        ingredientes.clear()

        # Traer ingredientes desde bd (se asume cantidad ya guardada en KG)
        try:
            ingredientes_bd = obtener_conformacion_receta(receta[1])  # devuelve [(materia, cantidad, costo), ...]
            for materia, cantidad, costo in ingredientes_bd:
                cantidad_f = float(cantidad)   # cantidad en KG (según convención)
                costo_f = float(costo)
                ingredientes.append((materia, cantidad_f, costo_f))
                tabla.insert("", "end", values=(materia, f"{cantidad_f:.4f}", f"${costo_f:.2f}"))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los ingredientes:\n{e}", parent=ventana)
            return

        # Recalcular totales con los ingredientes cargados
        actualizar_totales()

    # Bind del combobox a la función load
    combo_recetas.bind("<<ComboboxSelected>>", lambda e: cargar_receta_seleccionada())

# Fin de abrir_recetas

  
 