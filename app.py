import streamlit as st
import numpy as np

# Importamos las herramientas que creamos en la carpeta utils
from utils.calculations import equilibrio, construir_desde_puntos
from utils.components import load_css

# Importamos las pestañas que creamos en la carpeta views
from views.mercado import render_mercado
from views.elasticidad import render_elasticidad
from views.precio_maximo import render_precio_maximo
from views.precio_minimo import render_precio_minimo
from views.impuestos import render_impuestos
from views.subsidios import render_subsidios
from views.cuotas import render_cuotas
from views.dashboard import render_dashboard

# 1. Configuración de página (Restauramos el menú superior quitando menu_items={})
st.set_page_config(
    page_title="Simulador de Mercado - UNSTA",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded" # Fuerza a que la barra lateral inicie abierta
)

# Cargamos los estilos personalizados
load_css()

# 2. Encabezado principal
st.markdown("""
<div class="main-header">
  <h1>📈 Simulador de Mercado — Economía para Ingenieros</h1>
  <p>Facultad de Ingeniería · UNSTA · Prof. Raúl García</p>
</div>
""", unsafe_allow_html=True)

# 3. Barra lateral para entrada de datos
with st.sidebar:
    st.markdown("## ⚙️ Configurar Mercado")
    metodo = st.radio("Método de ingreso", ["Forma algebraica", "Desde dos puntos"])
    st.markdown("---")

    if metodo == "Forma algebraica":
        st.markdown("**Demanda:** Qd = a − b·P")
        a = st.number_input("a (intercepto demanda)", value=1000.0, step=10.0)
        b = st.number_input("b (pendiente demanda)", value=30.0, step=1.0, min_value=0.01)
        st.markdown("**Oferta:** Qo = c + d·P")
        c = st.number_input("c (intercepto oferta)", value=0.0, step=10.0)
        d = st.number_input("d (pendiente oferta)", value=20.0, step=1.0, min_value=0.01)
        valid = True
    else:
        st.markdown("**Demanda — dos puntos**")
        col1, col2 = st.columns(2)
        dp1p, dp2p = col1.number_input("P₁ (dem)", value=10.0), col1.number_input("P₂ (dem)", value=30.0)
        dp1q, dp2q = col2.number_input("Q₁ (dem)", value=700.0), col2.number_input("Q₂ (dem)", value=100.0)

        st.markdown("**Oferta — dos puntos**")
        col3, col4 = st.columns(2)
        op1p, op2p = col3.number_input("P₁ (ofe)", value=5.0), col3.number_input("P₂ (ofe)", value=25.0)
        op1q, op2q = col4.number_input("Q₁ (ofe)", value=100.0), col4.number_input("Q₂ (ofe)", value=500.0)

        a, b = construir_desde_puntos(dp1p, dp1q, dp2p, dp2q, "demanda")
        c, d = construir_desde_puntos(op1p, op1q, op2p, op2q, "oferta")

        if a is None:
            st.error("Error: Puntos inválidos.")
            valid = False
        else:
            valid = True
            st.info(f"Deducido: Qd={a:.1f}-{b:.1f}P | Qo={c:.1f}+{d:.1f}P")

    st.markdown("---")
    st.caption("Ingeniería Informática — UNSTA")

# 4. Cálculos Globales
if not valid:
    st.stop()

P_eq, Q_eq = equilibrio(a, b, c, d)
if P_eq is None or Q_eq < 0:
    st.error("No existe un equilibrio válido con estos datos.")
    st.stop()

p_min_graf = max(0, -c/d if d != 0 else 0)
p_max_graf = max(a/b, P_eq * 2, 50)
precios = np.linspace(p_min_graf, p_max_graf, 400)
Qd_vals = np.clip(a - b * precios, 0, None)
Qo_vals = np.clip(c + d * precios, 0, None)

# 5. Definición de Pestañas
tabs = st.tabs([
    "📊 Mercado", 
    "📐 Elasticidad", 
    "🔴 Precio Máximo", 
    "🟢 Precio Mínimo", 
    "💰 Impuestos", 
    "🎁 Subsidios", 
    "📦 Cuotas", 
    "📈 Dashboard"
])

# 6. Renderizado de cada módulo
with tabs[0]: render_mercado(a, b, c, d, P_eq, Q_eq, precios, Qd_vals, Qo_vals)
with tabs[1]: render_elasticidad(a, b, P_eq, Q_eq, precios, Qd_vals, Qo_vals)
with tabs[2]: render_precio_maximo(a, b, c, d, P_eq, Q_eq, precios, Qd_vals, Qo_vals)
with tabs[3]: render_precio_minimo(a, b, c, d, P_eq, Q_eq, precios, Qd_vals, Qo_vals)
with tabs[4]: render_impuestos(a, b, c, d, P_eq, Q_eq, precios, Qd_vals, Qo_vals)
with tabs[5]: render_subsidios(a, b, c, d, P_eq, Q_eq, precios, Qd_vals, Qo_vals)
with tabs[6]: render_cuotas(a, b, c, d, P_eq, Q_eq, precios, Qd_vals, Qo_vals)
with tabs[7]: render_dashboard(a, b, c, d, P_eq, Q_eq)