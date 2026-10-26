"""reporte_online.py: total de ventas hechas por la tienda online."""

from src.reporte_ventas import total_por_canal


def total_ventas_online(ventas: list[dict]) -> float:
    return total_por_canal(ventas, "online", incluye_envio=True)
