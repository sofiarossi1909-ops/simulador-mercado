import streamlit as st
from utils.components import card, fig_base, COLORS
import plotly.graph_objects as go

def render_cuotas(a, b, c, d, P_eq, Q_eq, precios, Qd_vals, Qo_vals):
    st.markdown("### 📦 Cuota de Producción")

    Q_cuota = st.slider("Cuota (máximo permitido)", min_value=1.0, max_value=float(Q_eq * 1.5), value=float(Q_eq * 0.75), step=1.0)

    Pd_cuota = (a - Q_cuota) / b if b != 0 else 0
    Ps_cuota = (Q_cuota - c) / d if d != 0 else 0
    renta = max(0, Pd_cuota - Ps_cuota)

    fig7 = fig_base("Mercado con Cuota de Producción", Qd_vals, Qo_vals, precios, Q_eq, P_eq)
    fig7.add_vline(x=Q_cuota, line_dash="dash", line_color=COLORS["cuota"], line_width=2.5, annotation_text=f"Cuota={Q_cuota:.0f}")
    
    fig7.add_trace(go.Scatter(x=[Q_cuota, Q_cuota], y=[Pd_cuota, Ps_cuota], mode="markers+text", marker=dict(size=12, color=[COLORS["demanda"], COLORS["oferta"]]), text=[f"Pd=${Pd_cuota:.2f}", f"Ps=${Ps_cuota:.2f}"], textposition=["top right", "bottom right"], name="Precios"))
    
    if renta > 0 and Q_cuota < Q_eq:
        fig7.add_shape(type="rect", x0=0, x1=Q_cuota, y0=Ps_cuota, y1=Pd_cuota, fillcolor="rgba(0,188,212,0.2)", line_width=0)
    
    st.plotly_chart(fig7, use_container_width=True)

    if Q_cuota < Q_eq: st.markdown('<div class="warning-box">⚠️ <b>Cuota obligatoria.</b> Genera una renta extraordinaria para los productores y pérdida de eficiencia social.</div>', unsafe_allow_html=True)
    else: st.markdown('<div class="success-box">✅ <b>No obligatoria.</b> La cuota es mayor al equilibrio, el mercado opera libremente.</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: card("Cuota Impuesta", f"{Q_cuota:.0f}", "purple")
    with c2: card("Pd (Compradores)", f"${Pd_cuota:.2f}", "red")
    with c3: card("Ps (Costo prod.)", f"${Ps_cuota:.2f}", "green")
    with c4:
        if Q_cuota < Q_eq: card("Renta Total", f"${renta * Q_cuota:,.2f}", "purple")