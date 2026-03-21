import csv
import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox
from statistics import mean, stdev

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def validar_estudiante_fila(fila, linea):
    if len(fila) != 4:
        raise ValueError(f"Línea {linea}: debe tener 4 columnas (nombre, cal1, cal2, cal3).")
    nombre, *calificaciones = fila
    if not nombre.strip():
        raise ValueError(f"Línea {linea}: nombre vacío.")
    notas = []
    for i, valor in enumerate(calificaciones, start=1):
        try:
            nota = float(valor)
        except ValueError:
            raise ValueError(f"Línea {linea}, cal{i}: '{valor}' no es número.")
        if not (0 <= nota <= 100):
            raise ValueError(f"Línea {linea}, cal{i}: {nota} fuera de 0-100.")
        notas.append(nota)
    return nombre.strip(), notas


def leer_csv_ruta(ruta_archivo):
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"No existe el archivo: {ruta_archivo}")

    estudiantes = []
    with open(ruta_archivo, newline="", encoding="utf-8") as archivo:
        lector = csv.reader(archivo)
        for linea, fila in enumerate(lector, start=1):
            if not fila or all(c.strip() == "" for c in fila):
                continue
            nombre, notas = validar_estudiante_fila(fila, linea)
            promedio = mean(notas)
            estudiantes.append({"nombre": nombre, "notas": notas, "promedio": promedio})

    if len(estudiantes) != 20:
        raise ValueError(f"Se esperaban 20 estudiantes, se encontraron {len(estudiantes)}.")

    return estudiantes


def calcular_estadisticas(estudiantes):
    promedios = [e["promedio"] for e in estudiantes]
    promedio_general = mean(promedios)
    desviacion = stdev(promedios)
    return len(estudiantes), promedio_general, desviacion, promedios


def crear_grafica(estudiantes, promedio_general, canvas_widget):
    nombres = [e["nombre"] for e in estudiantes]
    promedios = [e["promedio"] for e in estudiantes]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(nombres, promedios, color="skyblue", edgecolor="black")
    ax.axhline(promedio_general, color="red", linestyle="--", linewidth=2,
               label=f"Promedio general {promedio_general:.2f}")
    ax.set_xlabel("Estudiantes")
    ax.set_ylabel("Promedio")
    ax.set_title("Promedio por estudiante")
    ax.set_xticklabels(nombres, rotation=45, ha="right")
    ax.set_ylim(0, 100)
    ax.legend()
    fig.tight_layout()

    if canvas_widget.get_tk_widget() is not None:
        canvas_widget.get_tk_widget().destroy()

    chart = FigureCanvasTkAgg(fig, master=frame_grafica)
    chart.draw()
    chart.get_tk_widget().pack(fill=tk.BOTH, expand=1)
    return chart


def mostrar_resultados(total, promedio_general, desviacion):
    lbl_total_valor.config(text=str(total))
    lbl_promedio_valor.config(text=f"{promedio_general:.2f}")
    lbl_desviacion_valor.config(text=f"{desviacion:.2f}")


def procesar_archivo():
    ruta = filedialog.askopenfilename(
        title="Seleccionar CSV de calificaciones",
        filetypes=[("CSV", "*.csv"), ("Todos", "*.*")]
    )
    if not ruta:
        return
    try:
        estudiantes = leer_csv_ruta(ruta)
        total, promedio_general, desviacion, _ = calcular_estadisticas(estudiantes)
        mostrar_resultados(total, promedio_general, desviacion)
        global canvas
        canvas = crear_grafica(estudiantes, promedio_general, canvas)
    except Exception as e:
        messagebox.showerror("Error", str(e))


def generar_csv_ejemplo():
    ruta = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV", "*.csv")],
        title="Guardar CSV de ejemplo"
    )
    if not ruta:
        return

    with open(ruta, mode="w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        for i in range(1, 21):
            nombre = f"Estudiante_{i:02d}"
            cal1 = round(random.uniform(55, 100), 1)
            cal2 = round(random.uniform(55, 100), 1)
            cal3 = round(random.uniform(55, 100), 1)
            escritor.writerow([nombre, cal1, cal2, cal3])

    messagebox.showinfo("Éxito", f"Ejemplo de CSV guardado en:\n{ruta}")


def main():
    global ventana, lbl_total_valor, lbl_promedio_valor, lbl_desviacion_valor, frame_grafica, canvas
    ventana = tk.Tk()
    ventana.title("Analizador de calificaciones")
    ventana.geometry("1100x700")

    boton_abrir = tk.Button(ventana, text="Seleccionar archivo CSV", command=procesar_archivo, width=25)
    boton_abrir.pack(pady=8)

    boton_ejemplo = tk.Button(ventana, text="Generar CSV de ejemplo", command=generar_csv_ejemplo, width=25)
    boton_ejemplo.pack(pady=8)

    panel_info = tk.Frame(ventana)
    panel_info.pack(pady=8)

    tk.Label(panel_info, text="Total estudiantes:").grid(row=0, column=0, sticky="w", padx=8)
    lbl_total_valor = tk.Label(panel_info, text="-")
    lbl_total_valor.grid(row=0, column=1, sticky="w")

    tk.Label(panel_info, text="Promedio general:").grid(row=1, column=0, sticky="w", padx=8)
    lbl_promedio_valor = tk.Label(panel_info, text="-")
    lbl_promedio_valor.grid(row=1, column=1, sticky="w")

    tk.Label(panel_info, text="Desviación estándar:").grid(row=2, column=0, sticky="w", padx=8)
    lbl_desviacion_valor = tk.Label(panel_info, text="-")
    lbl_desviacion_valor.grid(row=2, column=1, sticky="w")

    frame_grafica = tk.Frame(ventana, relief=tk.RIDGE, borderwidth=2)
    frame_grafica.pack(fill=tk.BOTH, expand=1, padx=8, pady=8)

    canvas = FigureCanvasTkAgg(plt.figure(), master=frame_grafica)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

    ventana.mainloop()


if __name__ == "__main__":
    main()