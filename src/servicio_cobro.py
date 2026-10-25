"""servicio_cobro.py: cobro de pedidos del Food Store.

Calcula el total de un pedido con los productos del catálogo y lo cobra
a través de una pasarela de pagos externa. La pasarela se recibe por
constructor (inyección de dependencias): en producción es el cliente
real de la API de pagos y en las pruebas se reemplaza por un doble.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.catalogo import ErrorDominio, Producto


class PasarelaDePagos(Protocol):
    """Contrato de la API externa de pagos.

    El cobro se hace en dos pasos: primero se autoriza el monto sobre la
    tarjeta y, solo si fue aprobado, se captura (se hace efectivo).
    """

    def autorizar(self, monto: float, token_tarjeta: str) -> dict: ...

    def capturar(self, id_autorizacion: str) -> dict: ...


class PagoRechazado(Exception):
    """La pasarela respondió, pero no aprobó el pago."""


class PasarelaNoDisponible(Exception):
    """La pasarela no respondió. No se realizó ningún cobro."""


@dataclass(frozen=True)
class Comprobante:
    id_transaccion: str
    monto: float


class ServicioDeCobro:

    def __init__(self, pasarela: PasarelaDePagos) -> None:
        self._pasarela = pasarela

    def calcular_total(self, items: list[tuple[Producto, float]]) -> float:
        """Suma el precio final de cada línea del pedido."""
        if not items:
            raise ErrorDominio("El pedido no tiene productos.")
        total = 0.0
        for producto, cantidad in items:
            if not producto.disponible:
                raise ErrorDominio(f"'{producto.nombre}' no está disponible.")
            total += producto.precio_final(cantidad)
        return round(total, 2)

    def cobrar(
        self, items: list[tuple[Producto, float]], token_tarjeta: str
    ) -> Comprobante:
        """Valida el pedido, autoriza el total y, si se aprueba, lo captura.

        Si el pedido es inválido, la pasarela no se contacta.
        """
        total = self.calcular_total(items)

        try:
            autorizacion = self._pasarela.autorizar(total, token_tarjeta)
        except TimeoutError as error:
            raise PasarelaNoDisponible(
                "La pasarela de pagos no respondió. No se realizó ningún cobro."
            ) from error

        if autorizacion["estado"] != "aprobado":
            motivo = autorizacion.get("motivo", "sin motivo informado")
            raise PagoRechazado(f"Pago rechazado: {motivo}.")

        self._pasarela.capturar(autorizacion["id"])
        return Comprobante(id_transaccion=autorizacion["id"], monto=total)
