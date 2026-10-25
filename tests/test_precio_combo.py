"""Punto 1: suite de pruebas unitarias de ProductoCombo.precio_final.

Regla bajo prueba: el precio final de un combo es la suma del precio
final de una unidad de cada componente, con el descuento del combo
aplicado, multiplicada por la cantidad. La cantidad tiene que ser un
entero mayor o igual a 1.
"""

import pytest

from src.catalogo import (
    Categoria,
    ErrorDominio,
    ProductoCombo,
    ProductoPorPeso,
    ProductoSimple,
    UnidadMedida,
)


def test_combo_aplica_el_descuento_sobre_la_suma_de_sus_componentes():
    # Arrange
    combos = Categoria("Combos")
    hamburguesa = ProductoSimple("Hamburguesa", 4500.0, 20, combos)
    papas = ProductoSimple("Papas fritas", 2000.0, 30, combos)
    gaseosa = ProductoSimple("Gaseosa 500 ml", 1500.0, 50, combos)
    combo = ProductoCombo("Combo clásico", [hamburguesa, papas, gaseosa], 0.10, combos)

    # Act
    precio = combo.precio_final(1)

    # Assert
    assert precio == pytest.approx(7200.0)


def test_combo_multiplica_el_precio_por_la_cantidad_pedida():
    # Arrange
    combos = Categoria("Combos")
    hamburguesa = ProductoSimple("Hamburguesa", 4500.0, 20, combos)
    papas = ProductoSimple("Papas fritas", 2000.0, 30, combos)
    combo = ProductoCombo("Combo simple", [hamburguesa, papas], 0.10, combos)

    # Act
    precio = combo.precio_final(3)

    # Assert
    assert precio == pytest.approx(17550.0)


def test_combo_sin_descuento_cobra_la_suma_exacta_de_sus_componentes():
    # Arrange
    combos = Categoria("Combos")
    hamburguesa = ProductoSimple("Hamburguesa", 4500.0, 20, combos)
    gaseosa = ProductoSimple("Gaseosa 500 ml", 1500.0, 50, combos)
    combo = ProductoCombo("Combo sin promo", [hamburguesa, gaseosa], 0.0, combos)

    # Act
    precio = combo.precio_final(1)

    # Assert
    assert precio == pytest.approx(6000.0)


def test_combo_con_producto_por_peso_toma_una_unidad_de_medida():
    # Arrange
    fiambreria = Categoria("Fiambrería")
    kilo = UnidadMedida("kilogramo", "kg", "masa")
    queso = ProductoPorPeso("Queso de máquina", 8000.0, 5.5, fiambreria, kilo)
    pan = ProductoSimple("Pan de campo", 1200.0, 15, fiambreria)
    combo = ProductoCombo("Picada para dos", [queso, pan], 0.20, fiambreria)

    # Act
    precio = combo.precio_final(1)

    # Assert
    assert precio == pytest.approx(7360.0)


def test_combo_acepta_una_cantidad_entera_expresada_como_float():
    # Arrange
    combos = Categoria("Combos")
    hamburguesa = ProductoSimple("Hamburguesa", 4500.0, 20, combos)
    papas = ProductoSimple("Papas fritas", 2000.0, 30, combos)
    combo = ProductoCombo("Combo simple", [hamburguesa, papas], 0.10, combos)

    # Act
    precio = combo.precio_final(2.0)

    # Assert
    assert precio == pytest.approx(11700.0)


def test_combo_rechaza_cantidad_cero():
    # Arrange
    combos = Categoria("Combos")
    hamburguesa = ProductoSimple("Hamburguesa", 4500.0, 20, combos)
    papas = ProductoSimple("Papas fritas", 2000.0, 30, combos)
    combo = ProductoCombo("Combo simple", [hamburguesa, papas], 0.10, combos)

    # Act
    with pytest.raises(ErrorDominio) as error:
        combo.precio_final(0)

    # Assert
    assert "entero >= 1" in str(error.value)


def test_combo_rechaza_cantidad_negativa():
    # Arrange
    combos = Categoria("Combos")
    hamburguesa = ProductoSimple("Hamburguesa", 4500.0, 20, combos)
    papas = ProductoSimple("Papas fritas", 2000.0, 30, combos)
    combo = ProductoCombo("Combo simple", [hamburguesa, papas], 0.10, combos)

    # Act
    with pytest.raises(ErrorDominio) as error:
        combo.precio_final(-2)

    # Assert
    assert "entero >= 1" in str(error.value)


def test_combo_rechaza_cantidad_con_decimales():
    # Arrange
    combos = Categoria("Combos")
    hamburguesa = ProductoSimple("Hamburguesa", 4500.0, 20, combos)
    papas = ProductoSimple("Papas fritas", 2000.0, 30, combos)
    combo = ProductoCombo("Combo simple", [hamburguesa, papas], 0.10, combos)

    # Act
    with pytest.raises(ErrorDominio) as error:
        combo.precio_final(1.5)

    # Assert
    assert "entero >= 1" in str(error.value)


def test_combo_rechaza_cantidad_que_no_es_numerica():
    # Arrange
    combos = Categoria("Combos")
    hamburguesa = ProductoSimple("Hamburguesa", 4500.0, 20, combos)
    papas = ProductoSimple("Papas fritas", 2000.0, 30, combos)
    combo = ProductoCombo("Combo simple", [hamburguesa, papas], 0.10, combos)

    # Act
    with pytest.raises(ErrorDominio) as error:
        combo.precio_final("2")

    # Assert
    assert "numérica" in str(error.value)
