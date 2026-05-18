import streamlit as st
from utils.components import card, fig_base, COLORS
import plotly.graph_objects as go

def render_mercado(a, b, c, d, P_eq, Q_eq, precios, Qd_vals, Qo_vals):
    st.markdown("### 📊 Mercado Competitivo")
    
    fig = fig_base("Equilibrio de Mercado", Qd_vals, Qo_vals, precios, Q_eq, P_eq)
    fig.add_shape(type="line", x0=0, y0=P_eq, x1=Q_eq, y1=P_eq, line=dict(dash="dot", color=COLORS["eq"], width=1.5))
    fig.add_shape(type="line", x0=Q_eq, y0=0, x1=Q_eq, y1=P_eq, line=dict(dash="dot", color=COLORS["eq"], width=1.5))
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="section-title">Funciones</div>', unsafe_allow_html=True)
        st.info(f"**Demanda:** Qd = {a:.2f} − {b:.2f}·P")
        st.success(f"**Oferta:** Qo = {c:.2f} + {d:.2f}·P")
    with col2:
        st.markdown('<div class="section-title">Equilibrio</div>', unsafe_allow_html=True)
        card("Precio (P*)", f"${P_eq:.4f}", "orange")
        card("Cantidad (Q*)", f"{Q_eq:.2f}", "green")
    with col3:
        st.markdown('<div class="section-title">Derivación analítica</div>', unsafe_allow_html=True)
        st.markdown(f"**1.** {a:.2f} − {b:.2f}P = {c:.2f} + {d:.2f}P<br>**2.** {a-c:.2f} = {b+d:.2f}P<br>**3. P* = {P_eq:.4f}**<br>**4.** Q* = {c:.2f} + {d:.2f}({P_eq:.4f}) = **{Q_eq:.2f}**", unsafe_allow_html=True)