Desarrolla una aplicación gráfica de escritorio en Python 3.12 para analizar calificaciones de estudiantes.

Objetivo:
Crear un programa con interfaz gráfica que lea un archivo CSV con datos de 20 estudiantes, calcule estadísticas básicas y muestre una gráfica clara.

Requisitos funcionales:
1. La aplicación debe permitir seleccionar un archivo CSV desde la interfaz.
2. El archivo debe contener exactamente 20 estudiantes.
3. El formato del archivo debe ser:
   nombre,cal1,cal2,cal3
4. Para cada estudiante, calcula su promedio individual.
5. Calcula el promedio general del grupo usando los promedios individuales.
6. Calcula la desviación estándar de los promedios individuales del grupo.
7. Muestra en pantalla:
   - total de estudiantes,
   - promedio general,
   - desviación estándar.
8. Genera una gráfica de barras con el promedio de cada estudiante.
9. En la gráfica agrega una línea horizontal para representar el promedio general del grupo.
10. Incluye un botón o función para generar automáticamente un archivo CSV de ejemplo con 20 estudiantes y datos ficticios válidos.

Requisitos técnicos:
- Usa Python.
- Usa Tkinter para la interfaz gráfica.
- Usa matplotlib para la gráfica.
- Usa csv o pandas para la lectura del archivo.
- Usa statistics para el cálculo de promedio y desviación estándar, o implementa el cálculo de forma clara y correcta.
- El programa debe poder ejecutarse directamente con un archivo principal.

Requisitos de calidad:
- Aplica KISS y DRY.
- Divide la solución en funciones pequeñas y claras.
- Usa nombres descriptivos en español.
- Valida errores comunes:
  - archivo inexistente,
  - formato incorrecto,
  - número distinto de 20 estudiantes,
  - calificaciones no numéricas,
  - calificaciones fuera del rango 0 a 100.
- Muestra mensajes de error amigables en la interfaz.
- Incluye comentarios solo cuando aporten claridad.
- Incluye una función main().

Entregables esperados:
1. Código completo del programa.
2. Ejemplo del archivo CSV de prueba.
3. Instrucciones breves para ejecutar el programa.
4. Explicación corta de cómo se calcula el promedio general y la desviación estándar.