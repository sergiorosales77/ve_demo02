import csv
import os
import pytest

from analizador_calificaciones import (
    validar_estudiante_fila,
    leer_csv_ruta,
    calcular_estadisticas,
)


def test_validar_estudiante_fila_valida():
    fila = ["Juan", "80", "90", "100"]
    nombre, notas = validar_estudiante_fila(fila, 1)
    assert nombre == "Juan"
    assert notas == [80.0, 90.0, 100.0]


def test_validar_estudiante_fila_formato_incorrecto():
    with pytest.raises(ValueError, match=r"debe tener 4 columnas"):
        validar_estudiante_fila(["A", "1", "2"], 1)


def test_validar_estudiante_fila_nombre_vacio():
    with pytest.raises(ValueError, match=r"nombre vacío"):
        validar_estudiante_fila(["", "50", "60", "70"], 1)


def test_validar_estudiante_fila_nota_no_numero():
    with pytest.raises(ValueError, match=r"no es número"):
        validar_estudiante_fila(["Ana", "10", "B", "30"], 1)


def test_validar_estudiante_fila_nota_fuera_rango():
    with pytest.raises(ValueError, match=r"fuera de 0-100"):
        validar_estudiante_fila(["Ana", "10", "120", "30"], 1)


def test_leer_csv_ruta_existe_y_n_20_estudiantes(tmp_path):
    ruta = tmp_path / "estudiantes.csv"
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for i in range(20):
            writer.writerow([f"Estudiante{i+1}", 70 + i, 75 + i, 80 + i])

    estudiantes = leer_csv_ruta(str(ruta))
    assert len(estudiantes) == 20
    assert estudiantes[0]["nombre"] == "Estudiante1"
    assert estudiantes[-1]["notas"] == [89.0, 94.0, 99.0]


def test_leer_csv_ruta_cantidad_incorrecta(tmp_path):
    ruta = tmp_path / "estudiantes_menos.csv"
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for i in range(10):
            writer.writerow([f"Estudiante{i+1}", 70, 80, 90])

    with pytest.raises(ValueError, match=r"Se esperaban 20 estudiantes"):
        leer_csv_ruta(str(ruta))


def test_calcular_estadisticas_basico():
    estudiantes = [
        {"nombre": "A", "notas": [80, 90, 100], "promedio": 90},
        {"nombre": "B", "notas": [70, 80, 90], "promedio": 80},
    ]
    total, promedio_general, desviacion, promedios = calcular_estadisticas(estudiantes)
    assert total == 2
    assert promedio_general == 85
    assert promedios == [90, 80]
    assert pytest.approx(desviacion, rel=1e-6) == 7.0710678118654755
