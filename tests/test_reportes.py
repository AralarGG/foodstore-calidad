"""Pruebas de los reportes de ventas por canal.

Son la red de seguridad de la refactorización: tienen que pasar igual
antes y después de reescribir los reportes.
"""

import pytest

from src.reporte_mostrador import total_ventas_mostrador
from src.reporte_online import total_ventas_online


def venta(canal, medio_pago, monto, cuotas=1, envio=0.0, anulada=False):
    return {
        "anulada": anulada,
        "canal": canal,
        "medio_pago": medio_pago,
        "monto": monto,
        "cuotas": cuotas,
        "envio": envio,
    }


@pytest.mark.parametrize(
    "medio_pago, monto, cuotas, esperado",
    [
        ("efectivo", 10000.0, 1, 9500.0),
        ("efectivo", 30000.0, 1, 27000.0),
        ("debito", 10000.0, 1, 10000.0),
        ("debito", 30000.0, 1, 28500.0),
        ("credito", 10000.0, 1, 10000.0),
        ("credito", 10000.0, 3, 11500.0),
        ("credito", 10000.0, 12, 18400.0),
        ("transferencia", 10000.0, 1, 10000.0),
    ],
)
def test_mostrador_aplica_la_regla_de_cada_medio_de_pago(
    medio_pago, monto, cuotas, esperado
):
    # Arrange
    ventas = [venta("mostrador", medio_pago, monto, cuotas)]

    # Act
    total = total_ventas_mostrador(ventas)

    # Assert
    assert total == pytest.approx(esperado)


def test_mostrador_ignora_las_ventas_online():
    # Arrange
    ventas = [
        venta("mostrador", "debito", 5000.0),
        venta("online", "debito", 8000.0, envio=1500.0),
    ]

    # Act
    total = total_ventas_mostrador(ventas)

    # Assert
    assert total == pytest.approx(5000.0)


def test_mostrador_no_suma_ventas_anuladas():
    # Arrange
    ventas = [
        venta("mostrador", "debito", 5000.0),
        venta("mostrador", "debito", 7000.0, anulada=True),
    ]

    # Act
    total = total_ventas_mostrador(ventas)

    # Assert
    assert total == pytest.approx(5000.0)


def test_online_suma_el_envio_al_monto_neto():
    # Arrange
    ventas = [venta("online", "efectivo", 10000.0, envio=1500.0)]

    # Act
    total = total_ventas_online(ventas)

    # Assert
    assert total == pytest.approx(11000.0)


def test_online_con_credito_en_cuotas():
    # Arrange
    ventas = [venta("online", "credito", 20000.0, cuotas=6, envio=2500.0)]

    # Act
    total = total_ventas_online(ventas)

    # Assert
    assert total == pytest.approx(28500.0)


def test_total_de_un_canal_sin_ventas_es_cero():
    # Arrange
    ventas = [venta("mostrador", "efectivo", 10000.0)]

    # Act
    total = total_ventas_online(ventas)

    # Assert
    assert total == 0.0
