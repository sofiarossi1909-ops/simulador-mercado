def equilibrio(a, b, c, d):
    if (b + d) == 0:
        return None, None
    p = (a - c) / (b + d)
    q = c + d * p
    return p, q

def curva_demanda_inv(a, b, q):
    return (a - q) / b if b != 0 else 0

def curva_oferta_inv(c, d, q):
    return (q - c) / d if d != 0 else 0

def construir_desde_puntos(p1, q1, p2, q2, tipo="demanda"):
    if p2 == p1:
        return None, None
    pendiente = (q2 - q1) / (p2 - p1)
    intercepto = q1 - pendiente * p1
    if tipo == "demanda":
        return intercepto, -pendiente
    else:
        return intercepto, pendiente