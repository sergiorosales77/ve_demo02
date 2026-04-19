#!/usr/bin/env python3
"""
Compresor de PDF inteligente.
Reduce el tamaño de un PDF a menos de 10 MB preservando la calidad del texto.

Estrategia:
1. Primero intenta recomprimir con Ghostscript (mejor calidad).
2. Si no está disponible, usa pikepdf para optimizar streams.
3. Reduce la resolución de imágenes embebidas de forma progresiva
   hasta alcanzar el objetivo, manteniendo el texto como vectores.
"""

import os
import shutil
import subprocess
import sys
import tempfile

import pikepdf
from PIL import Image

OBJETIVO_MB = 10
OBJETIVO_BYTES = OBJETIVO_MB * 1024 * 1024


def tamano_mb(ruta: str) -> float:
    """Devuelve el tamaño del archivo en MB."""
    return os.path.getsize(ruta) / (1024 * 1024)


def ghostscript_disponible() -> bool:
    """Verifica si Ghostscript está instalado."""
    return shutil.which("gs") is not None


def comprimir_con_ghostscript(entrada: str, salida: str, dpi: int = 220, jpeg_quality: int = 88) -> bool:
    """
    Comprime con Ghostscript controlando resolución y JPEG de forma fina.
    Esto evita saltos bruscos de calidad típicos de /ebook o /screen.
    """
    try:
        cmd = [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.5",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            "-dPDFSETTINGS=/default",
            "-dColorConversionStrategy=/LeaveColorUnchanged",
            "-sColorConversionStrategy=LeaveColorUnchanged",
            "-dAutoRotatePages=/None",
            "-dDownsampleColorImages=true",
            "-dDownsampleGrayImages=true",
            "-dDownsampleMonoImages=true",
            "-dColorImageDownsampleType=/Bicubic",
            "-dGrayImageDownsampleType=/Bicubic",
            "-dMonoImageDownsampleType=/Subsample",
            f"-dColorImageResolution={dpi}",
            f"-dGrayImageResolution={dpi}",
            "-dMonoImageResolution=600",
            "-dAutoFilterColorImages=false",
            "-dAutoFilterGrayImages=false",
            "-dColorImageFilter=/DCTEncode",
            "-dGrayImageFilter=/DCTEncode",
            f"-dJPEGQ={jpeg_quality}",
            "-dOptimize=true",
            "-dEmbedAllFonts=true",
            "-dSubsetFonts=true",
            "-dCompressFonts=true",
            "-dDetectDuplicateImages=true",
            f"-sOutputFile={salida}",
            entrada,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return os.path.exists(salida) and os.path.getsize(salida) > 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def comprimir_con_pikepdf(entrada: str, salida: str) -> bool:
    """Comprime usando pikepdf: lineariza, recomprime streams y elimina duplicados."""
    try:
        with pikepdf.open(entrada) as pdf:
            pdf.save(
                salida,
                linearize=True,
                compress_streams=True,
                stream_decode_level=pikepdf.StreamDecodeLevel.generalized,
                object_stream_mode=pikepdf.ObjectStreamMode.generate,
                recompress_flate=True,
            )
        return os.path.exists(salida) and os.path.getsize(salida) > 0
    except Exception as e:
        print(f"  Error con pikepdf: {e}")
        return False


def reducir_imagenes_pdf(entrada: str, salida: str, factor_escala: float = 0.5, calidad_jpeg: int = 60) -> bool:
    """
    Abre el PDF y reduce las imágenes embebidas manteniendo el texto vectorial.
    - factor_escala: reduce dimensiones de la imagen (0.5 = mitad).
    - calidad_jpeg: calidad JPEG para imágenes recomprimidas (1-95).
    """
    try:
        with pikepdf.open(entrada) as pdf:
            imagenes_procesadas = 0
            for pagina in pdf.pages:
                if "/Resources" not in pagina:
                    continue
                resources = pagina["/Resources"]
                if "/XObject" not in resources:
                    continue
                xobjects = resources["/XObject"]
                for nombre_obj in list(xobjects.keys()):
                    xobj = xobjects[nombre_obj]
                    if not isinstance(xobj, pikepdf.Stream):
                        continue
                    try:
                        if xobj.get("/Subtype") != "/Image":
                            continue
                    except Exception:
                        continue

                    try:
                        original_color_space = xobj.get("/ColorSpace")
                        if isinstance(original_color_space, pikepdf.Name):
                            original_color_space_name = str(original_color_space)
                        else:
                            original_color_space_name = ""

                        # Evita cambios de color en espacios complejos (ICCBased/Indexed/etc.).
                        if original_color_space_name and original_color_space_name not in (
                            "/DeviceRGB",
                            "/DeviceGray",
                            "/DeviceCMYK",
                        ):
                            continue

                        ancho = int(xobj.get("/Width", 0))
                        alto = int(xobj.get("/Height", 0))
                        if ancho == 0 or alto == 0:
                            continue

                        nuevo_ancho = max(int(ancho * factor_escala), 50)
                        nuevo_alto = max(int(alto * factor_escala), 50)

                        # Extraer imagen raw
                        raw_data = xobj.read_raw_bytes()
                        filtro = xobj.get("/Filter", "")

                        # Intentar reconstruir imagen desde bytes
                        pil_img = None
                        if str(filtro) in ("/DCTDecode", "/JPXDecode"):
                            # JPEG o JPEG2000
                            import io
                            try:
                                pil_img = Image.open(io.BytesIO(raw_data))
                            except Exception:
                                continue
                        else:
                            # Intentar decodificar con pikepdf
                            try:
                                from pikepdf import PdfImage
                                pdf_img = PdfImage(xobj)
                                pil_img = pdf_img.as_pil_image()
                            except Exception:
                                continue

                        if pil_img is None:
                            continue

                        # Redimensionar con filtro de alta calidad
                        pil_img = pil_img.resize(
                            (nuevo_ancho, nuevo_alto),
                            Image.LANCZOS,
                        )

                        # Mantiene colores originales en RGB/Gray/CMYK; elimina alpha solo cuando aplica.
                        if pil_img.mode in ("RGBA", "LA"):
                            pil_img = pil_img.convert("RGB")
                        elif pil_img.mode == "P":
                            pil_img = pil_img.convert("RGB")
                        elif pil_img.mode not in ("RGB", "L", "CMYK"):
                            pil_img = pil_img.convert("RGB")

                        # Guardar como JPEG comprimido
                        import io
                        buffer = io.BytesIO()
                        pil_img.save(buffer, format="JPEG", quality=calidad_jpeg, optimize=True)
                        jpeg_data = buffer.getvalue()

                        # Reemplazar la imagen en el PDF
                        xobj.write(jpeg_data, filter=pikepdf.Name("/DCTDecode"))
                        xobj["/Width"] = nuevo_ancho
                        xobj["/Height"] = nuevo_alto
                        if pil_img.mode == "CMYK":
                            xobj["/ColorSpace"] = pikepdf.Name("/DeviceCMYK")
                        elif pil_img.mode == "L":
                            xobj["/ColorSpace"] = pikepdf.Name("/DeviceGray")
                        else:
                            xobj["/ColorSpace"] = pikepdf.Name("/DeviceRGB")
                        xobj["/BitsPerComponent"] = 8
                        if "/SMask" in xobj:
                            del xobj["/SMask"]
                        if "/DecodeParms" in xobj:
                            del xobj["/DecodeParms"]

                        imagenes_procesadas += 1
                    except Exception:
                        continue

            pdf.save(
                salida,
                linearize=True,
                compress_streams=True,
                object_stream_mode=pikepdf.ObjectStreamMode.generate,
                recompress_flate=True,
            )
            print(f"  Imágenes recomprimidas: {imagenes_procesadas}")
        return os.path.exists(salida) and os.path.getsize(salida) > 0
    except Exception as e:
        print(f"  Error al reducir imágenes: {e}")
        return False


def comprimir_pdf(ruta_entrada: str, ruta_salida: str | None = None) -> str:
    """Comprime priorizando calidad visual y tamaño cercano al objetivo."""
    ruta_entrada = os.path.abspath(ruta_entrada)
    if not os.path.exists(ruta_entrada):
        raise FileNotFoundError(f"No se encontró: {ruta_entrada}")

    tamano_original = tamano_mb(ruta_entrada)
    print(f"Archivo: {os.path.basename(ruta_entrada)}")
    print(f"Tamaño original: {tamano_original:.2f} MB")

    if tamano_original <= OBJETIVO_MB:
        print(f"El archivo ya está por debajo de {OBJETIVO_MB} MB. No se requiere compresión.")
        if ruta_salida:
            shutil.copy2(ruta_entrada, ruta_salida)
            return ruta_salida
        return ruta_entrada

    if ruta_salida is None:
        base, ext = os.path.splitext(ruta_entrada)
        ruta_salida = f"{base}_comprimido{ext}"

    dir_temp = tempfile.mkdtemp(prefix="pdf_compress_")
    candidatos: list[tuple[str, float, str]] = []

    def registrar_candidato(candidato: str, etapa: str) -> None:
        if not os.path.exists(candidato):
            return
        t = tamano_mb(candidato)
        reduccion = ((tamano_original - t) / tamano_original * 100)
        candidatos.append((candidato, t, etapa))
        print(f"  ✓ {etapa}: {t:.2f} MB (reducción: {reduccion:.1f}%)")

    def seleccionar_mejor_candidato() -> tuple[str, float, str]:
        if not candidatos:
            return ruta_entrada, tamano_original, "sin_compresion"

        dentro_objetivo = [c for c in candidatos if c[1] <= OBJETIVO_MB]
        if dentro_objetivo:
            # Evita sobrecomprimir: prefiere quedar cerca del objetivo (>= 85% del objetivo).
            rango_ideal = [c for c in dentro_objetivo if c[1] >= OBJETIVO_MB * 0.85]
            if rango_ideal:
                return max(rango_ideal, key=lambda x: x[1])
            return max(dentro_objetivo, key=lambda x: x[1])

        # Si no se alcanzó el objetivo, elegir la mayor reducción posible.
        return min(candidatos, key=lambda x: x[1])

    try:
        # --- Paso 1: Optimización sin pérdida fuerte ---
        print("\n[Paso 1] Optimización de estructura (pikepdf)...")
        temp_pike = os.path.join(dir_temp, "pikepdf_opt.pdf")
        if comprimir_con_pikepdf(ruta_entrada, temp_pike):
            registrar_candidato(temp_pike, "pikepdf streams")

        # --- Paso 2: Ghostscript con perfiles suaves ---
        if ghostscript_disponible():
            print("\n[Paso 2] Compresión con Ghostscript (calidad controlada)...")
            perfiles_gs = [
                (300, 95, "300dpi Q95"),
                (260, 92, "260dpi Q92"),
                (230, 88, "230dpi Q88"),
                (200, 84, "200dpi Q84"),
                (180, 80, "180dpi Q80"),
                (160, 76, "160dpi Q76"),
            ]
            for dpi, q, nombre in perfiles_gs:
                temp_gs = os.path.join(dir_temp, f"gs_{dpi}_{q}.pdf")
                if comprimir_con_ghostscript(ruta_entrada, temp_gs, dpi=dpi, jpeg_quality=q):
                    registrar_candidato(temp_gs, f"Ghostscript {nombre}")
        else:
            print("\n[Info] Ghostscript no encontrado. Instálalo para mejor compresión:")
            print("  macOS:  brew install ghostscript")
            print("  Linux:  sudo apt install ghostscript")

        mejor_actual, tam_mejor_actual, _ = seleccionar_mejor_candidato()

        # --- Paso 3: Ajuste fino de imágenes (solo si todavía no llega al objetivo) ---
        if tam_mejor_actual > OBJETIVO_MB:
            print("\n[Paso 3] Ajuste fino de imágenes (evitando pixelado agresivo)...")
            base_ajuste = mejor_actual
            configuraciones = [
                (0.95, 90, "95% tamaño, JPEG 90"),
                (0.90, 88, "90% tamaño, JPEG 88"),
                (0.85, 85, "85% tamaño, JPEG 85"),
                (0.80, 82, "80% tamaño, JPEG 82"),
                (0.75, 78, "75% tamaño, JPEG 78"),
                (0.70, 75, "70% tamaño, JPEG 75"),
            ]

            for i, (escala, calidad, desc) in enumerate(configuraciones):
                temp_img = os.path.join(dir_temp, f"img_fino_{i}.pdf")
                print(f"\n  Intentando: {desc}")
                if reducir_imagenes_pdf(base_ajuste, temp_img, escala, calidad):
                    registrar_candidato(temp_img, f"Imágenes ({desc})")

        # --- Selección final: cercanía al objetivo con máxima calidad ---
        mejor_archivo, tamano_final, etapa_final = seleccionar_mejor_candidato()

        # --- Resultado final ---
        shutil.copy2(mejor_archivo, ruta_salida)
        tamano_final = tamano_mb(ruta_salida)
        reduccion = ((tamano_original - tamano_final) / tamano_original * 100)

        print(f"\n{'=' * 50}")
        print(f"Original:  {tamano_original:.2f} MB")
        print(f"Final:     {tamano_final:.2f} MB")
        print(f"Reducción: {reduccion:.1f}%")
        print(f"Método:    {etapa_final}")
        print(f"Archivo:   {ruta_salida}")

        if tamano_final > OBJETIVO_MB:
            print(f"\n⚠ No se logró reducir a menos de {OBJETIVO_MB} MB.")
            print("  Sugerencias:")
            print("  - Instala Ghostscript si no lo tienes.")
            print("  - Sube temporalmente el objetivo (ej. 12 MB) y vuelve a intentar.")
            print("  - El PDF puede tener imágenes escaneadas de muy alta densidad.")

        return ruta_salida

    finally:
        shutil.rmtree(dir_temp, ignore_errors=True)


def main():
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    import threading

    root = tk.Tk()
    root.title("Compresor PDF")
    root.geometry("520x240")
    root.resizable(False, False)

    # Lleva la ventana al frente de forma explícita al iniciar.
    root.lift()
    root.attributes("-topmost", True)
    root.after(400, lambda: root.attributes("-topmost", False))
    root.focus_force()

    objetivo_var = tk.StringVar(value="10")
    estado_var = tk.StringVar(value="Presiona el botón para elegir el PDF.")

    cont = ttk.Frame(root, padding=16)
    cont.pack(fill="both", expand=True)

    ttk.Label(cont, text="Tamaño objetivo (MB):").pack(anchor="w")
    entrada_objetivo = ttk.Entry(cont, textvariable=objetivo_var, width=10)
    entrada_objetivo.pack(anchor="w", pady=(4, 12))

    ttk.Label(
        cont,
        text="Selecciona un PDF y luego dónde guardar el archivo comprimido.",
    ).pack(anchor="w", pady=(0, 8))

    lbl_estado = ttk.Label(cont, textvariable=estado_var)
    lbl_estado.pack(anchor="w", pady=(0, 12))

    barra = ttk.Progressbar(cont, mode="indeterminate")
    barra.pack(fill="x", pady=(0, 12))

    def finalizar_ok(resultado: str):
        barra.stop()
        btn_comprimir.config(state="normal")
        tam = tamano_mb(resultado)
        estado_var.set(f"Listo: {tam:.2f} MB")
        messagebox.showinfo(
            "Completado",
            f"PDF comprimido guardado en:\n{resultado}\n\nTamaño final: {tam:.2f} MB",
            parent=root,
        )

    def finalizar_error(mensaje: str):
        barra.stop()
        btn_comprimir.config(state="normal")
        estado_var.set("Error durante la compresión.")
        messagebox.showerror("Error", mensaje, parent=root)

    def ejecutar_compresion():
        try:
            objetivo = float(objetivo_var.get().strip())
            if objetivo <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Dato inválido", "Ingresa un número válido mayor a 0 para MB.", parent=root)
            return

        ruta_entrada = filedialog.askopenfilename(
            parent=root,
            title="Selecciona el PDF a comprimir",
            filetypes=[("Archivos PDF", "*.pdf")],
        )
        if not ruta_entrada:
            return

        base, ext = os.path.splitext(ruta_entrada)
        ruta_salida = filedialog.asksaveasfilename(
            parent=root,
            title="Guardar PDF comprimido como",
            defaultextension=".pdf",
            initialfile=f"{os.path.basename(base)}_comprimido{ext}",
            initialdir=os.path.dirname(ruta_entrada),
            filetypes=[("Archivos PDF", "*.pdf")],
        )
        if not ruta_salida:
            return

        global OBJETIVO_MB, OBJETIVO_BYTES
        OBJETIVO_MB = objetivo
        OBJETIVO_BYTES = int(OBJETIVO_MB * 1024 * 1024)

        btn_comprimir.config(state="disabled")
        estado_var.set("Comprimiendo... esto puede tardar unos minutos.")
        barra.start(12)

        def tarea():
            try:
                resultado = comprimir_pdf(ruta_entrada, ruta_salida)
                root.after(0, lambda: finalizar_ok(resultado))
            except Exception as e:
                root.after(0, lambda: finalizar_error(str(e)))

        threading.Thread(target=tarea, daemon=True).start()

    btn_comprimir = ttk.Button(cont, text="Seleccionar PDF y Comprimir", command=ejecutar_compresion)
    btn_comprimir.pack(anchor="w")

    root.mainloop()


if __name__ == "__main__":
    main()
