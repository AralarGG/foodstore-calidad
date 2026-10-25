"""reporte_ventas.py: cálculo común de los reportes de ventas del Food Store.

Reúne en un solo lugar la regla de monto neto según el medio de pago, que
antes estaba copiada en el reporte de mostrador y en el de la tienda online.
Los coeficientes pasan a ser datos en una tabla en lugar de if anidados.
"""

UMBRAL_MONTO_ALTO = 20000

# medio de pago: (coeficiente para montos normales, coeficiente para montos altos)
COEFICIENTES_POR_MEDIO = {
    "efectivo": (0.95, 0.90),
    "debito": (1.00, 0.95),
}

RECARGO_POR_CUOTA = 0.05
RECARGO_POR_CUOTA_LARGA = 0.07
CUOTAS_LARGAS_DESDE = 7


def coeficiente_credito(cuotas: int) -> float:
    """Recargo por pagar en cuotas: 5% por cuota, 7% desde las 7 cuotas."""
    if cuotas >= CUOTAS_LARGAS_DESDE:
        return 1 + RECARGO_POR_CUOTA_LARGA * cuotas
    if cuotas > 1:
        return 1 + RECARGO_POR_CUOTA * cuotas
    return 1.0


def monto_neto(venta: dict) -> float:
    """Monto de una venta con el descuento o recargo de su medio de pago."""
    monto = venta["monto"]
    if venta["medio_pago"] == "credito":
        return monto * coeficiente_credito(venta["cuotas"])
    normal, alto = COEFICIENTES_POR_MEDIO.get(venta["medio_pago"], (1.0, 1.0))
    return monto * (alto if monto > UMBRAL_MONTO_ALTO else normal)


def total_por_canal(ventas: list[dict], canal: str, incluye_envio: bool) -> float:
    """Suma el monto neto de las ventas no anuladas de un canal."""
    total = 0.0
    for venta in ventas:
        if venta["anulada"] or venta["canal"] != canal:
            continue
        total += monto_neto(venta)
        if incluye_envio:
            total += venta["envio"]
    return round(total, 2)
