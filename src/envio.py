"""envio.py: costo de envío de un pedido del Food Store."""

from src.catalogo import ErrorDominio

TARIFAS_POR_ZONA = {
    "centro": 1500.0,
    "periferia": 2500.0,
    "interior": 6000.0,
}
ENVIO_GRATIS_DESDE = 30000.0
DESCUENTO_CLIENTE_FRECUENTE = 0.5


def calcular_costo_envio(
    subtotal: float, zona: str, retira_en_local: bool, cliente_frecuente: bool
) -> float:
    """Costo de envío según zona, monto del pedido y tipo de cliente.

    Reglas:
    - Si el cliente retira en el local, el envío no se cobra.
    - La zona tiene que existir en la tabla de tarifas.
    - Envío gratis desde ENVIO_GRATIS_DESDE, salvo para el interior.
    - El cliente frecuente paga la mitad del costo que le corresponda.
    """
    if retira_en_local:
        return 0.0
    if zona not in TARIFAS_POR_ZONA:
        raise ErrorDominio(f"Zona de envío desconocida: {zona!r}.")
    costo = TARIFAS_POR_ZONA[zona]
    if subtotal >= ENVIO_GRATIS_DESDE and zona != "interior":
        costo = 0.0
    if cliente_frecuente:
        costo = costo * (1 - DESCUENTO_CLIENTE_FRECUENTE)
    return costo
