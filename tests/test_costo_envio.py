"""Punto 3: casos de prueba de calcular_costo_envio.

Decisiones de la función:
  D1: retira_en_local
  D2: zona not in TARIFAS_POR_ZONA
  D3: subtotal >= ENVIO_GRATIS_DESDE and zona != "interior"
  D4: cliente_frecuente

Los casos marcados con @pytest.mark.sentencias son los tres mínimos que
ejecutan todas las líneas (100% de sentencias). Con los siete casos se
recorren las dos salidas, verdadera y falsa, de cada decisión (100% de
ramas).
"""

import pytest

from src.catalogo import ErrorDominio
from src.envio import calcular_costo_envio


@pytest.mark.sentencias
def test_c1_retiro_en_local_no_paga_envio():
    # Arrange
    subtotal, zona = 12000.0, "periferia"

    # Act
    costo = calcular_costo_envio(
        subtotal, zona, retira_en_local=True, cliente_frecuente=False
    )

    # Assert
    assert costo == 0.0


@pytest.mark.sentencias
def test_c2_zona_desconocida_lanza_error():
    # Arrange
    subtotal, zona = 12000.0, "marte"

    # Act
    with pytest.raises(ErrorDominio) as error:
        calcular_costo_envio(
            subtotal, zona, retira_en_local=False, cliente_frecuente=False
        )

    # Assert
    assert "Zona de envío desconocida" in str(error.value)


@pytest.mark.sentencias
def test_c3_envio_gratis_y_cliente_frecuente():
    # Arrange
    subtotal, zona = 35000.0, "centro"

    # Act
    costo = calcular_costo_envio(
        subtotal, zona, retira_en_local=False, cliente_frecuente=True
    )

    # Assert
    assert costo == 0.0


def test_c4_pedido_chico_de_cliente_comun_paga_tarifa_completa():
    # Arrange
    subtotal, zona = 10000.0, "periferia"

    # Act
    costo = calcular_costo_envio(
        subtotal, zona, retira_en_local=False, cliente_frecuente=False
    )

    # Assert
    assert costo == 2500.0


def test_c5_interior_no_tiene_envio_gratis_aunque_supere_el_monto():
    # Arrange
    subtotal, zona = 35000.0, "interior"

    # Act
    costo = calcular_costo_envio(
        subtotal, zona, retira_en_local=False, cliente_frecuente=False
    )

    # Assert
    assert costo == 6000.0


def test_c6_cliente_frecuente_paga_la_mitad_de_un_costo_real():
    # Arrange
    subtotal, zona = 10000.0, "interior"

    # Act
    costo = calcular_costo_envio(
        subtotal, zona, retira_en_local=False, cliente_frecuente=True
    )

    # Assert
    assert costo == 3000.0


def test_c7_subtotal_justo_en_el_limite_tiene_envio_gratis():
    # Arrange
    subtotal, zona = 30000.0, "centro"

    # Act
    costo = calcular_costo_envio(
        subtotal, zona, retira_en_local=False, cliente_frecuente=False
    )

    # Assert
    assert costo == 0.0
