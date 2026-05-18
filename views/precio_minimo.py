import streamlit as st
from utils.components import card, fig_base, COLORS
import plotly.graph_objects as go

def render_precio_minimo(a, b, c, d, P_eq, Q_eq, precios, Qd_vals, Qo_vals):
    st.markdown("### 🟢 Precio Mínimo (Piso de Precio)")

    P_min = st.slider("Precio Mínimo ($)", min_value=0.0, max_value=float(P_eq * 2), value=float(P_eq * 1.4), step=float(P_eq / 100))

    Qd_min = max(0, a - b * P_min)
    Qo_min = max(0, c + d * P_min)
    excedente = max(0, Qo_min - Qd_min)
    es_obligatorio = P_min > P_eq

    fig4 = fig_base("Mercado con Precio Mínimo", Qd_vals, Qo_vals, precios, Q_eq, P_eq)
    fig4.add_hline(y=P_min, line_dash="dash", line_color=COLORS["oferta"], annotation_text=f"Min: ${P_min:.2f}")
    
    if es_obligatorio and excedente > 0:
        fig4.add_vrect(x0=Qd_min, x1=Qo_min, fillcolor=COLORS["shade_excedente"], line_width=0, annotation_text="Excedente")
        fig4.add_trace(go.Scatter(x=[Qd_min, Qo_min], y=[P_min, P_min], mode="markers", marker=dict(size=10, color=COLORS["oferta"]), name=f"Qd={Qd_min:.0f} | Qo={Qo_min:.0f}"))
    
    st.plotly_chart(fig4, use_container_width=True)

    if es_obligatorio: st.markdown('<div class="warning-box">⚠️ <b>Obligatorio</b> (está por encima del equilibrio). Genera excedente.</div>', unsafe_allow_html=True)
    else: st.markdown('<div class="success-box">✅ <b>No obligatorio</b> (está por debajo del equilibrio). El mercado opera al precio P*.</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: card("P* Original", f"${P_eq:.2f}", "orange")
    with c2: card("Q Demandada", f"{Qd_min:.2f}", "red")
    with c3: card("Q Ofrecida", f"{Qo_min:.2f}", "green")
    with c4:
        if es_obligatorio: card("Excedente generado", f"{excedente:.2f}", "green")