Actúa como un desarrollador senior de Python con enfoque en Clean Code.

Construye una aplicación gráfica de escritorio en Python 3.12 usando Tkinter y matplotlib.

Caso:
La aplicación debe leer un archivo CSV con 20 estudiantes. Cada fila contiene:
nombre,cal1,cal2,cal3

Comportamiento esperado:
- Permitir al usuario seleccionar el archivo CSV.
- Validar que existan exactamente 20 registros.
- Validar que las calificaciones sean numéricas y estén entre 0 y 100.
- Calcular el promedio de cada estudiante.
- Calcular el promedio general del grupo a partir de los promedios individuales.
- Calcular la desviación estándar de los promedios del grupo.
- Mostrar los resultados numéricos en la ventana.
- Dibujar una gráfica de barras con los promedios de los 20 estudiantes.
- Dibujar una línea horizontal con el promedio general.
- Mostrar la desviación estándar como dato visible en la interfaz.
- Agregar un botón para generar un archivo CSV de ejemplo con 20 estudiantes ficticios.

Diseño del software:
- Separa la lógica en funciones:
  - cargar_archivo()
  - validar_datos()
  - calcular_promedios()
  - calcular_estadisticas()
  - generar_archivo_ejemplo()
  - graficar_resultados()
  - main()
- Mantén el código simple, legible y mantenible.
- No agregues dependencias innecesarias.
- Incluye manejo de errores y mensajes amigables para el usuario.

Entrega:
- Código completo listo para ejecutar.
- Ejemplo de archivo CSV.
- Instrucciones de ejecución.