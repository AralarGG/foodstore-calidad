"""reporte_mostrador.py: total de ventas cobradas en el mostrador del local."""

from src.reporte_ventas import total_por_canal


def total_ventas_mostrador(ventas: list[dict]) -> float:
    return total_por_canal(ventas, "mostrador", incluye_envio=False)
