"""reporte_mostrador.py: total de ventas cobradas en el mostrador del local."""


def total_ventas_mostrador(ventas):
    total = 0
    for v in ventas:
        if v["anulada"] == True:
            continue
        if v["canal"] == "mostrador":
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
    return round(total, 2)
