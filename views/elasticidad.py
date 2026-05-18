import streamlit as st
from utils.components import card, fig_base
import plotly.graph_objects as go

def render_elasticidad(a, b, P_eq, Q_eq, precios, Qd_vals, Qo_vals):
    st.markdown("### 📐 Elasticidad-Precio de la Demanda (Punto Medio)")
    
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        P1_e = st.number_input("Precio P₁", value=float(round(P_eq * 0.8, 2)), key="P1e")
        Q1_e = st.number_input("Cantidad Q₁", value=float(round(a - b * P1_e, 2)), key="Q1e")
    with col_e2:
        P2_e = st.number_input("Precio P₂", value=float(round(P_eq * 1.2, 2)), key="P2e")
        Q2_e = st.number_input("Cantidad Q₂", value=float(round(a - b * P2_e, 2)), key="Q2e")

    fig2 = fig_base("Elasticidad — Puntos seleccionados", Qd_vals, Qo_vals, precios, Q_eq, P_eq)
    fig2.add_trace(go.Scatter(x=[Q1_e, Q2_e], y=[P1_e, P2_e], name="Puntos A y B", mode="markers+text", marker=dict(size=13, color="#ab47bc", symbol="diamond"), text=["A", "B"], textposition="top right", textfont=dict(size=13, color="#ab47bc")))
    st.plotly_chart(fig2, use_container_width=True)

    if P2_e == P1_e:
        st.error("P₁ y P₂ no pueden ser iguales.")
        return

    dQ, dP = Q2_e - Q1_e, P2_e - P1_e
    Q_med, P_med = (Q1_e + Q2_e) / 2, (P1_e + P2_e) / 2
    
    if Q_med == 0 or P_med == 0:
        st.error("Promedio de Q o P es cero. Revisá los puntos.")
        return
        
    Ed = (dQ / Q_med) / (dP / P_med)

    c1, c2, c3 = st.columns(3)
    with c1:
        card("Elasticidad |Ed|", f"{abs(Ed):.4f}", "purple")
    with c2:
        IT_A, IT_B = P1_e * Q1_e, P2_e * Q2_e
        card("Ingreso Total (A)", f"${IT_A:,.2f}", "green" if IT_A >= IT_B else "red")
        card("Ingreso Total (B)", f"${IT_B:,.2f}", "green" if IT_B >= IT_A else "red")
    with c3:
        if abs(Ed) > 1: st.markdown('<div class="info-box"><b>🔵 ELÁSTICA</b><br>⬇️ El IT disminuye si el P sube.</div>', unsafe_allow_html=True)
        elif abs(Ed) < 1: st.markdown('<div class="warning-box"><b>🟠 INELÁSTICA</b><br>⬆️ El IT aumenta si el P sube.</div>', unsafe_allow_html=True)
        else: st.markdown('<div class="success-box"><b>🟢 UNITARIA</b><br>➡️ El IT no cambia.</div>', unsafe_allow_html=True)