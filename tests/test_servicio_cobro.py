"""Punto 2: dobles de prueba para la pasarela de pagos externa.

Los Stubs son clases escritas a mano que devuelven respuestas fijas:
sirven para probar cómo reacciona ServicioDeCobro ante cada respuesta
posible de la API. El Mock (unittest.mock) registra las llamadas que
recibe: sirve para auditar que el servicio respete el protocolo de
cobro (qué métodos llama, con qué argumentos, en qué orden y cuántas
veces).
"""

from unittest.mock import Mock, call

import pytest

from src.catalogo import Categoria, ErrorDominio, ProductoSimple
from src.servicio_cobro import (
    Comprobante,
    PagoRechazado,
    PasarelaDePagos,
    PasarelaNoDisponible,
    ServicioDeCobro,
)

TOKEN = "tok_visa_4242"


def pedido_de_prueba():
    """Pedido válido: 2 hamburguesas (9000) + 1 gaseosa (1500) = 10500."""
    rotiseria = Categoria("Rotisería")
    hamburguesa = ProductoSimple("Hamburguesa", 4500.0, 20, rotiseria)
    gaseosa = ProductoSimple("Gaseosa 500 ml", 1500.0, 50, rotiseria)
    return [(hamburguesa, 2), (gaseosa, 1)]


# Stubs: respuestas enlatadas, sin lógica ni registro de llamadas


class StubPasarelaAprobada:
    def autorizar(self, monto, token_tarjeta):
        return {"estado": "aprobado", "id": "AUT-001"}

    def capturar(self, id_autorizacion):
        return {"estado": "capturado"}


class StubPasarelaRechazada:
    def autorizar(self, monto, token_tarjeta):
        return {"estado": "rechazado", "motivo": "fondos insuficientes"}

    def capturar(self, id_autorizacion):
        return {"estado": "capturado"}


class StubPasarelaSinRespuesta:
    def autorizar(self, monto, token_tarjeta):
        raise TimeoutError("sin respuesta en 30 s")

    def capturar(self, id_autorizacion):
        raise TimeoutError("sin respuesta en 30 s")


def test_stub_pago_aprobado_devuelve_comprobante_con_el_total():
    # Arrange
    servicio = ServicioDeCobro(StubPasarelaAprobada())
    items = pedido_de_prueba()

    # Act
    comprobante = servicio.cobrar(items, TOKEN)

    # Assert
    assert comprobante == Comprobante(id_transaccion="AUT-001", monto=10500.0)


def test_stub_pago_rechazado_lanza_error_con_el_motivo():
    # Arrange
    servicio = ServicioDeCobro(StubPasarelaRechazada())
    items = pedido_de_prueba()

    # Act
    with pytest.raises(PagoRechazado) as error:
        servicio.cobrar(items, TOKEN)

    # Assert
    assert "fondos insuficientes" in str(error.value)


def test_stub_pasarela_sin_respuesta_lanza_error_controlado():
    # Arrange
    servicio = ServicioDeCobro(StubPasarelaSinRespuesta())
    items = pedido_de_prueba()

    # Act
    with pytest.raises(PasarelaNoDisponible) as error:
        servicio.cobrar(items, TOKEN)

    # Assert
    assert "No se realizó ningún cobro" in str(error.value)
    assert isinstance(error.value.__cause__, TimeoutError)


# Mocks: registran cada llamada para verificar el protocolo de cobro


def crear_mock_pasarela(respuesta_autorizar):
    pasarela = Mock(spec=PasarelaDePagos)
    pasarela.autorizar.return_value = respuesta_autorizar
    pasarela.capturar.return_value = {"estado": "capturado"}
    return pasarela


def test_mock_autoriza_una_sola_vez_con_el_monto_exacto_del_pedido():
    # Arrange
    pasarela = crear_mock_pasarela({"estado": "aprobado", "id": "AUT-777"})
    servicio = ServicioDeCobro(pasarela)
    items = pedido_de_prueba()

    # Act
    servicio.cobrar(items, TOKEN)

    # Assert
    pasarela.autorizar.assert_called_once_with(10500.0, TOKEN)


def test_mock_captura_despues_de_autorizar_y_con_el_id_recibido():
    # Arrange
    pasarela = crear_mock_pasarela({"estado": "aprobado", "id": "AUT-777"})
    servicio = ServicioDeCobro(pasarela)
    items = pedido_de_prueba()

    # Act
    servicio.cobrar(items, TOKEN)

    # Assert
    assert pasarela.mock_calls == [
        call.autorizar(10500.0, TOKEN),
        call.capturar("AUT-777"),
    ]


def test_mock_no_captura_si_el_pago_fue_rechazado():
    # Arrange
    pasarela = crear_mock_pasarela({"estado": "rechazado", "motivo": "tarjeta vencida"})
    servicio = ServicioDeCobro(pasarela)
    items = pedido_de_prueba()

    # Act
    with pytest.raises(PagoRechazado):
        servicio.cobrar(items, TOKEN)

    # Assert
    pasarela.autorizar.assert_called_once()
    pasarela.capturar.assert_not_called()


def test_mock_no_contacta_la_pasarela_si_el_pedido_esta_vacio():
    # Arrange
    pasarela = crear_mock_pasarela({"estado": "aprobado", "id": "AUT-777"})
    servicio = ServicioDeCobro(pasarela)

    # Act
    with pytest.raises(ErrorDominio):
        servicio.cobrar([], TOKEN)

    # Assert
    assert pasarela.mock_calls == []


def test_mock_no_contacta_la_pasarela_si_un_producto_no_esta_disponible():
    # Arrange
    pasarela = crear_mock_pasarela({"estado": "aprobado", "id": "AUT-777"})
    servicio = ServicioDeCobro(pasarela)
    items = pedido_de_prueba()
    hamburguesa, _ = items[0]
    hamburguesa.deshabilitar()

    # Act
    with pytest.raises(ErrorDominio) as error:
        servicio.cobrar(items, TOKEN)

    # Assert
    assert "no está disponible" in str(error.value)
    assert pasarela.mock_calls == []
