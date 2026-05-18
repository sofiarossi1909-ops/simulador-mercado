import streamlit as st
import numpy as np
import plotly.graph_objects as go
from utils.calculations import equilibrio
from utils.components import card, fig_base, COLORS

def render_subsidios(a, b, c, d, P_eq, Q_eq, precios, Qd_vals, Qo_vals):
    st.markdown("### 🎁 Subsidios")

    col_s1, col_s2 = st.columns(2)
    with col_s1: tipo_sub = st.radio("Subsidio aplicado a:", ["Productores (s% sobre precio)", "Compradores (descuento precio)"])
    with col_s2: s_pct = st.slider("Subsidio (%)", 0, 80, 10, 1)

    s = s_pct / 100
    if "Productores" in tipo_sub:
        d_new = d * (1 + s)
        P_new_s, Q_new_s = equilibrio(a, b, c, d_new)
        Pc, Ps = P_new_s, P_new_s * (1 + s)
        curva_nueva_x = np.clip(c + d_new * precios, 0, None)
    else:
        a_new_s = a + b * s * P_eq
        P_new_s, Q_new_s = equilibrio(a_new_s, b, c, d)
        Pc, Ps = P_new_s - s * P_eq, P_new_s
        curva_nueva_x = np.clip(a_new_s - b * precios, 0, None)

    fig6 = fig_base("Efecto del Subsidio", Qd_vals, Qo_vals, precios, Q_eq, P_eq)
    fig6.add_trace(go.Scatter(x=curva_nueva_x, y=precios, name="Curva con subsidio", line=dict(color=COLORS["subsidio"], width=2, dash="dash")))
    fig6.add_trace(go.Scatter(x=[Q_new_s], y=[P_new_s], name="Nuevo Eq.", mode="markers", marker=dict(size=12, color=COLORS["subsidio"], symbol="star")))
    fig6.add_hline(y=Ps, line_dash="dot", line_color=COLORS["subsidio"], annotation_text=f"Ps ${Ps:.2f}")
    fig6.add_hline(y=Pc, line_dash="dot", line_color=COLORS["demanda"], annotation_text=f"Pc ${Pc:.2f}")
    st.plotly_chart(fig6, use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: card("Nueva Cantidad Q'", f"{Q_new_s:.2f}")
    with c2: card("Pagan Comprad.", f"${Pc:.2f}", "green")
    with c3: card("Reciben Product.", f"${Ps:.2f}", "purple")
    with c4: card("Costo Gobierno", f"${(Ps - Pc) * Q_new_s:,.2f}", "red")

    st.markdown('<div class="info-box"><b>Bienestar social:</b> El costo del gobierno es mayor que el beneficio conjunto de productores y consumidores (Pérdida irrecuperable de eficiencia).</div>', unsafe_allow_html=True)