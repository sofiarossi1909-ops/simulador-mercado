import streamlit as st

# Importamos la función card para darle color a las métricas
from utils.components import card 

def render_dashboard(a, b, c, d, P_eq, Q_eq):
    st.markdown("### 📈 Dashboard Resumen del Mercado Libre")
    
    dash_c1, dash_c2, dash_c3, dash_c4 = st.columns(4)
    
    # Usamos las tarjetas con colores en lugar del st.metric estándar
    with dash_c1: 
        card("Precio Equilibrio (P*)", f"${P_eq:.2f}", "orange")
    with dash_c2: 
        card("Cantidad Equilibrio (Q*)", f"{Q_eq:.0f}", "green")
    with dash_c3: 
        card("Ingreso Total en Eq.", f"${P_eq * Q_eq:,.2f}", "purple")
    with dash_c4: 
        card("Modelo", "Lineal Cerrado")

    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**📉 Demanda:** Qd = {a:.2f} - {b:.2f}P")
        st.write(f"- Demanda máxima a precio $0: **{a:.0f}** unid.")
        st.write(f"- Precio prohibitivo (nadie compra): **${a/b if b!=0 else 0:.2f}**")
        
    with col2:
        st.success(f"**🏭 Oferta:** Qo = {c:.2f} + {d:.2f}P")
        if c < 0: 
            st.write(f"- Precio mínimo exigido para producir: **${-c/d if d!=0 else 0:.2f}**")
        else: 
            st.write(f"- Oferta inicial garantizada a precio $0: **{c:.0f}** unid.")