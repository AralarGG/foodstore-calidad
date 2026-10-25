"""reporte_online.py: total de ventas hechas por la tienda online."""


def total_ventas_online(ventas):
    total = 0
    for v in ventas:
        if v["anulada"] == True:
            continue
        if v["canal"] == "online":
            if v["medio_pago"] == "efectivo":
                if v["monto"] > 20000:
                    total = total + v["monto"] * 0.90
                else:
                    total = total + v["monto"] * 0.95
            elif v["medio_pago"] == "debito":
                if v["monto"] > 20000:
                    total = total + v["monto"] * 0.95
                else:
                    total = total + v["monto"]
            elif v["medio_pago"] == "credito":
                if v["cuotas"] > 6:
                    total = total + v["monto"] * (1 + 0.07 * v["cuotas"])
                elif v["cuotas"] > 1:
                    total = total + v["monto"] * (1 + 0.05 * v["cuotas"])
                else:
                    total = total + v["monto"]
            else:
                total = total + v["monto"]
            total = total + v["envio"]
    return round(total, 2)
