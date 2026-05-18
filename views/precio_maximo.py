import streamlit as st
from utils.components import card, fig_base, COLORS
import plotly.graph_objects as go

def render_precio_maximo(a, b, c, d, P_eq, Q_eq, precios, Qd_vals, Qo_vals):
    st.markdown("### 🔴 Precio Máximo (Techo de Precio)")

    P_max = st.slider("Precio Máximo ($)", min_value=0.0, max_value=float(P_eq * 2), value=float(P_eq * 0.7), step=float(P_eq / 100))

    Qd_max = max(0, a - b * P_max)
    Qo_max = max(0, c + d * P_max)
    escasez = max(0, Qd_max - Qo_max)
    es_obligatorio = P_max < P_eq

    fig3 = fig_base("Mercado con Precio Máximo", Qd_vals, Qo_vals, precios, Q_eq, P_eq)
    fig3.add_hline(y=P_max, line_dash="dash", line_color=COLORS["interv"], annotation_text=f"Max: ${P_max:.2f}")
    
    if es_obligatorio and escasez > 0:
        fig3.add_vrect(x0=Qo_max, x1=Qd_max, fillcolor=COLORS["shade_escasez"], line_width=0, annotation_text="Escasez")
        fig3.add_trace(go.Scatter(x=[Qo_max, Qd_max], y=[P_max, P_max], mode="markers", marker=dict(size=10, color=COLORS["interv"]), name=f"Qo={Qo_max:.0f} | Qd={Qd_max:.0f}"))
    
    st.plotly_chart(fig3, use_container_width=True)

    if es_obligatorio: st.markdown('<div class="warning-box">⚠️ <b>Obligatorio</b> (está por debajo del equilibrio). Genera escasez.</div>', unsafe_allow_html=True)
    else: st.markdown('<div class="success-box">✅ <b>No obligatorio</b> (está por encima del equilibrio). El mercado opera al precio P*.</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: card("P* Original", f"${P_eq:.2f}", "orange")
    with c2: card("Q Demandada", f"{Qd_max:.2f}", "red")
    with c3: card("Q Ofrecida", f"{Qo_max:.2f}", "green")
    with c4:
        if es_obligatorio: card("Escasez generada", f"{escasez:.2f}", "red")