import streamlit as st
import numpy as np
import plotly.graph_objects as go
from utils.calculations import equilibrio
from utils.components import card, fig_base, COLORS

def render_impuestos(a, b, c, d, P_eq, Q_eq, precios, Qd_vals, Qo_vals):
    st.markdown("### 💰 Impuestos e Incidencia Fiscal")

    col1, col2 = st.columns(2)
    with col1: tipo_imp = st.radio("Aplicado a:", ["Vendedores (Oferta ↑)", "Compradores (Demanda ↓)"])
    with col2: t = st.slider("Monto del impuesto ($)", 0.0, float(P_eq*0.8), float(P_eq*0.12), step=0.1)

    # Cálculo
    if "Vendedores" in tipo_imp:
        P_new, Q_new = equilibrio(a, b, c - d*t, d)
        P_comp, P_vend = P_new, P_new - t
        curva_nueva_x = np.clip((c - d*t) + d * precios, 0, None)
    else:
        P_new, Q_new = equilibrio(a - b*t, b, c, d)
        P_comp, P_vend = P_new + t, P_new
        curva_nueva_x = np.clip((a - b*t) - b * precios, 0, None)

    # 1. GRÁFICO ARRIBA OCUPANDO TODO EL ANCHO
    fig5 = fig_base("Impacto del Impuesto", Qd_vals, Qo_vals, precios, Q_eq, P_eq)
    fig5.add_trace(go.Scatter(x=curva_nueva_x, y=precios, name="Curva desplazada", line=dict(color=COLORS["interv"], width=2, dash="dash")))
    fig5.add_trace(go.Scatter(x=[Q_new], y=[P_new], mode="markers", marker=dict(size=12, color=COLORS["interv"], symbol="x"), name="Nuevo Eq."))
    
    if Q_new > 0:
        fig5.add_hline(y=P_comp, line_dash="dot", annotation_text=f"Pd ${P_comp:.2f}")
        fig5.add_hline(y=P_vend, line_dash="dot", annotation_text=f"Ps ${P_vend:.2f}")
    
    st.plotly_chart(fig5, use_container_width=True)

    # 2. TARJETAS ABAJO DISTRIBUIDAS HORIZONTALMENTE
    st.markdown('<div class="section-title">Resultados del Impuesto</div>', unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    with m1: card("P* Original", f"${P_eq:.2f}", "orange")
    with m2: card("Nueva Cantidad", f"{Q_new:.2f}", "red")
    with m3: card("Pagan Comprad.", f"${P_comp:.2f}", "orange")
    with m4: card("Reciben Vended.", f"${P_vend:.2f}", "green")

    r1, r2, r3 = st.columns(3)
    with r1: card("Recaudación", f"${t*Q_new:,.2f}", "purple")
    inc_c, inc_v = (P_comp - P_eq) * Q_new, (P_eq - P_vend) * Q_new
    if inc_c + inc_v > 0:
        with r2: card("Absorbe Comprador", f"${inc_c:,.2f} ({inc_c/(inc_c+inc_v)*100:.0f}%)", "orange")
        with r3: card("Absorbe Vendedor", f"${inc_v:,.2f} ({inc_v/(inc_c+inc_v)*100:.0f}%)", "green")