import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="Simulador de Mercado - UNSTA",
    layout="wide"
)

# ─── Estilos ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    body {
        background: #f1f5f9;
    }
    .stApp {
        background: linear-gradient(180deg, #f4f7fc 0%, #eef3fb 45%, #f9fbff 100%);
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    div[data-testid="stSidebar"] > div:first-child {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 22px;
        padding: 16px 16px 20px 16px;
        box-shadow: 0 20px 40px rgba(15, 23, 42, 0.10);
        border: 1px solid rgba(29, 78, 216, 0.08);
    }
    div[data-testid="stSidebar"] .stMarkdown {
        color: #334155;
        font-size: .90rem;
        line-height: 1.4;
    }
    div[data-testid="stSidebar"] .sidebar-heading {
        font-size: 1rem;
        font-weight: 700;
        color: #1a237e;
        margin-bottom: 4px;
    }
    div[data-testid="stSidebar"] .sidebar-note {
        color: #475569;
        font-size: .85rem;
        line-height: 1.4;
        margin-bottom: 8px;
    }
    div[data-testid="stSidebar"] .sidebar-list {
        padding-left: 1rem;
        margin: 4px 0;
        color: #475569;
        font-size: .85rem;
        line-height: 1.4;
    }
    .main-header {
        background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #4527a0 100%);
        padding: 8px 14px;
        border-radius: 8px;
        margin-bottom: 8px;
        color: white;
        box-shadow: 0 4px 10px rgba(26, 35, 126, 0.1);
    }
    .main-header h1 { margin: 0; font-size: 1.25rem; line-height: 1.05; }
    .main-header p  { margin: 2px 0 0; opacity: .85; font-size: .8rem; }
    .module-heading {
        font-size: 1.05rem;
        font-weight: 700;
        color: #102a43;
        margin-bottom: 2px;
    }

    .metric-card {
        background: white;
        border-left: 4px solid #1a237e;
        border-radius: 8px;
        padding: 6px 10px;
        margin: 4px 0;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.05);
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 6px;
        min-height: 48px;
        width: 100%;
    }
    .metric-card.green  { border-color: #2e7d32; }
    .metric-card.orange { border-color: #e65100; }
    .metric-card.red    { border-color: #c62828; }
    .metric-card.purple { border-color: #6a1b9a; }

    .metric-label { display: block; font-size: .65rem; color: #475569; font-weight: 700;
                    text-transform: uppercase; letter-spacing: .05em; margin-bottom: 2px; }
    .metric-value { font-size: 1.05rem; font-weight: 800; color: #102a43; text-align: right; }
    .metric-card.green  .metric-value { color: #2e7d32; }
    .metric-card.orange .metric-value { color: #e65100; }
    .metric-card.red    .metric-value { color: #c62828; }
    .metric-card.purple .metric-value { color: #6a1b9a; }

    .metric-card .metric-text {
        flex: 1 1 50%;
        min-width: 0;
    }
    .metric-card .metric-value {
        flex: 0 0 auto;
        min-width: 80px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .result-panel {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 8px;
    }

    .info-box, .warning-box, .success-box {
        border-radius: 8px;
        padding: 8px 10px;
        margin: 6px 0;
        font-size: .85rem;
        line-height: 1.3;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.05);
    }
    .info-box { background: #e8eaf6; color: #172b4d; }
    .warning-box { background: #fff4e5; color: #b56012; }
    .success-box { background: #e8f5e9; color: #1b5e20; }

    .section-title {
        font-size: .90rem;
        font-weight: 700;
        color: #1a237e;
        border-left: 3px solid #1a237e;
        padding-left: 6px;
        margin: 8px 0 4px;
    }

    .stMarkdown h2, .stMarkdown h3 {
        color: #1a237e;
    }
    div[data-testid="stTabs"] button { font-weight: 700; }

    /* Bordes negros permanentes para todos los recuadros de ingreso de datos */
    div[data-baseweb="input"] > div {
        border: 1px solid #000000 !important;
        border-radius: 6px !important;
    }
    div[data-baseweb="input"] {
        border: 1px solid #000000 !important;
        border-radius: 6px !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>Simulador de Mercado interactivo</h1>
  <p>Economía para Ingenieros — UNSTA</p>
</div>
""", unsafe_allow_html=True)

# ─── Helpers ────────────────────────────────────────────────────────────────
def equilibrio(a, b, c, d):
    """Qd = a - b*P  |  Qo = c + d*P  →  P* = (a-c)/(b+d), Q* = c + d*P*"""
    if (b + d) == 0:
        return None, None
    p = (a - c) / (b + d)
    q = c + d * p
    return p, q

def curva_demanda_inv(a, b, q):
    """P a partir de Q en la demanda: P = (a-Q)/b"""
    return (a - q) / b if b != 0 else 0

def curva_oferta_inv(c, d, q):
    """P a partir de Q en la oferta: P = (Q-c)/d"""
    return (q - c) / d if d != 0 else 0

def construir_desde_puntos(p1, q1, p2, q2, tipo="demanda"):
    """Deduce a,b o c,d desde dos puntos."""
    if p2 == p1:
        return None, None
    pendiente = (q2 - q1) / (p2 - p1)   # dQ/dP
    intercepto = q1 - pendiente * p1
    if tipo == "demanda":
        # Qd = a - b*P  →  b = -pendiente, a = intercepto
        b = -pendiente
        a = intercepto
        return a, b
    else:
        # Qo = c + d*P  →  d = pendiente, c = intercepto
        d = pendiente
        c = intercepto
        return c, d

def card(label, value, color=""):
    st.markdown(
        f'<div class="metric-card {color}">'
        f'<div class="metric-text"><div class="metric-label">{label}</div></div>'
        f'<div class="metric-value">{value}</div>'
        f'</div>', unsafe_allow_html=True
    )


def card_grid(items):
    html = '<div class="result-panel">'
    for label, value, color in items:
        html += f'<div class="metric-card {color}"><div class="metric-text"><div class="metric-label">{label}</div></div><div class="metric-value">{value}</div></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

COLORS = dict(
    demanda="#1565c0", oferta="#2e7d32",
    eq="#e65100", interv="#c62828", subsidio="#6a1b9a",
    cuota="#00838f", shade_escasez="rgba(198,40,40,0.15)",
    shade_excedente="rgba(46,125,50,0.15)",
    shade_imp_comp="rgba(255,193,7,0.4)",
    shade_imp_vend="rgba(100,181,246,0.4)",
)

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR — entrada de funciones
# ═══════════════════════════════════════════════════════════════════════════
with st.expander("Configuración de las funciones de Oferta y Demanda", expanded=True):
    col_metodo, col_params = st.columns([1, 4])
    with col_metodo:
        metodo = st.radio("Método de ingreso", ["Algebraica", "Dos puntos"], key="metodo")
    
    with col_params:
        if metodo == "Algebraica":
            c1, c2, c3, c4 = st.columns(4)
            with c1: a = st.number_input("a (intercepto dem)", value=1000.0, step=10.0, format="%g")
            with c2: b = st.number_input("b (pendiente dem)", value=30.0, step=1.0, min_value=0.01, format="%g")
            with c3: c = st.number_input("c (intercepto ofe)", value=0.0, step=10.0, format="%g")
            with c4: d = st.number_input("d (pendiente ofe)", value=20.0, step=1.0, min_value=0.01, format="%g")
            valid = True
        else:
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                dp1p = st.number_input("P₁ (dem)", value=10.0, format="%g")
                op1p = st.number_input("P₁ (ofe)", value=5.0, format="%g")
            with c2:
                dp1q = st.number_input("Q₁ (dem)", value=700.0, format="%g")
                op1q = st.number_input("Q₁ (ofe)", value=100.0, format="%g")
            with c3:
                dp2p = st.number_input("P₂ (dem)", value=30.0, format="%g")
                op2p = st.number_input("P₂ (ofe)", value=25.0, format="%g")
            with c4:
                dp2q = st.number_input("Q₂ (dem)", value=100.0, format="%g")
                op2q = st.number_input("Q₂ (ofe)", value=500.0, format="%g")

            a_raw, b_raw = construir_desde_puntos(dp1p, dp1q, dp2p, dp2q, "demanda")
            c_raw, d_raw = construir_desde_puntos(op1p, op1q, op2p, op2q, "oferta")

            if a_raw is None or b_raw is None or c_raw is None or d_raw is None:
                st.error("Curva vertical (P₁ = P₂). Revisá los datos.")
                valid = False
                a = b = c = d = 1.0
            else:
                a, b, c, d = a_raw, b_raw, c_raw, d_raw
                valid = True
                st.info(f"Demanda: Qd = {a:.2f} − {b:.2f}·P | Oferta: Qo = {c:.2f} + {d:.2f}·P")

st.markdown("<br>", unsafe_allow_html=True)
tab_names = ["Mercado", "Elasticidad", "Precio Máximo", "Precio Mínimo", "Impuestos", "Subsidios", "Cuotas"]
tabs = st.tabs(tab_names)

# ═══════════════════════════════════════════════════════════════════════════
# Equilibrio base
# ═══════════════════════════════════════════════════════════════════════════
if not valid:
    st.stop()

P_eq, Q_eq = equilibrio(a, b, c, d)
if P_eq is None or Q_eq < 0:
    st.error("Las funciones ingresadas no generan un equilibrio válido (Q* < 0 o divisor = 0). Revisá los parámetros.")
    st.stop()

# Rango de precios para graficar
P_max_curva = a / b  # precio donde Qd = 0
P_min_oferta = -c / d if d != 0 else 0  # precio donde Qo = 0
P_range_max = max(P_max_curva, P_eq * 2, 50)
P_range_min = max(0, P_min_oferta)
precios = np.linspace(P_range_min, P_range_max, 400)

Qd_vals = a - b * precios
Qo_vals = c + d * precios
# Clip negativos
Qd_vals = np.clip(Qd_vals, 0, None)
Qo_vals = np.clip(Qo_vals, 0, None)

def fig_base(title=""):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=Qd_vals, y=precios, name="Demanda",
                             line=dict(color=COLORS["demanda"], width=2.5)))
    fig.add_trace(go.Scatter(x=Qo_vals, y=precios, name="Oferta",
                             line=dict(color=COLORS["oferta"], width=2.5)))
    fig.add_trace(go.Scatter(x=[Q_eq], y=[P_eq], name=f"Equilibrio (P={P_eq:.2f}, Q={Q_eq:.0f})",
                             mode="markers", marker=dict(color=COLORS["eq"], size=12, symbol="circle")))
    fig.update_layout(
        template="plotly_white",
        title=dict(text=title, font=dict(size=14, color="#1a237e")),
        title_x=0.02,
        title_y=0.96,
        title_xanchor="left",
        xaxis_title="Cantidad", yaxis_title="Precio",
        legend=dict(orientation="h", yanchor="bottom", y=1.14, xanchor="center", x=0.5,
                    bgcolor="rgba(255,255,255,0.94)", bordercolor="#dfe3e8", borderwidth=0.5,
                    font=dict(size=10)),
        plot_bgcolor="#fbfcfe", paper_bgcolor="#fbfcfe",
        height=450,
        margin=dict(l=40, r=20, t=50, b=25),
        hovermode="x unified",
    )
    fig.update_xaxes(gridcolor="#eeeeee", zeroline=True, zerolinecolor="#bbb")
    fig.update_yaxes(gridcolor="#eeeeee", zeroline=True, zerolinecolor="#bbb")
    return fig


# ══════════════════════════════════════════════════════
# TAB 1 — Mercado competitivo
# ══════════════════════════════════════════════════════
with tabs[0]:
    col_g, col_r = st.columns([2.5, 1])
    with col_g:
        fig = fig_base("Equilibrio de Mercado")
        fig.add_shape(type="line", x0=0, y0=P_eq, x1=Q_eq, y1=P_eq,
                      line=dict(dash="dot", color=COLORS["eq"], width=1.5))
        fig.add_shape(type="line", x0=Q_eq, y0=0, x1=Q_eq, y1=P_eq,
                      line=dict(dash="dot", color=COLORS["eq"], width=1.5))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})
    
    with col_r:
        st.markdown('<div class="section-title">Funciones</div>', unsafe_allow_html=True)
        st.markdown(f"**Qd** = {a:.1f} − {b:.1f}P")
        st.markdown(f"**Qo** = {c:.1f} + {d:.1f}P")
        st.markdown('<div class="section-title">Equilibrio</div>', unsafe_allow_html=True)
        card_grid([
            ("P*", f"${P_eq:.2f}", "orange"),
            ("Q*", f"{Q_eq:.0f}", ""),
        ])

# ══════════════════════════════════════════════════════
# TAB 2 — Elasticidad (método punto medio Mankiw)
# ══════════════════════════════════════════════════════
with tabs[1]:
    col_g2, col_r2 = st.columns([2.5, 1])
    with col_r2:
        st.markdown('<div class="section-title">Puntos de análisis</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            P1_e = st.number_input("P₁", value=float(round(P_eq * 0.8, 2)), key="P1e", format="%g")
            P2_e = st.number_input("P₂", value=float(round(P_eq * 1.2, 2)), key="P2e", format="%g")
        with c2:
            Q1_e = st.number_input("Q₁", value=float(round(a - b * P1_e, 2)), key="Q1e", format="%g")
            Q2_e = st.number_input("Q₂", value=float(round(a - b * P2_e, 2)), key="Q2e", format="%g")
    with col_g2:
        fig2 = fig_base("Elasticidad — Puntos A y B")
        fig2.add_trace(go.Scatter(
            x=[Q1_e, Q2_e], y=[P1_e, P2_e],
            name="Puntos", mode="markers+text",
            marker=dict(size=12, color="#9c27b0", symbol="diamond"),
            text=["A", "B"], textposition="top right",
            textfont=dict(size=11, color="#9c27b0")
        ))
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False, "responsive": True})
    
    with col_r2:
        if P2_e == P1_e:
            st.warning("P₁ = P₂")
        else:
            dQ = Q2_e - Q1_e
            dP = P2_e - P1_e
            Q_med = (Q1_e + Q2_e) / 2
            P_med = (P1_e + P2_e) / 2
            if Q_med != 0 and P_med != 0:
                Ed = (dQ / Q_med) / (dP / P_med)
                IT_A = P1_e * Q1_e
                IT_B = P2_e * Q2_e
                card_grid([
                    ("|Ed|", f"{abs(Ed):.3f}", "purple"),
                    ("IT_A", f"${IT_A:,.0f}", ""),
                    ("IT_B", f"${IT_B:,.0f}", ""),
                ])
                if abs(Ed) > 1:
                    st.markdown('<div class="info-box"><b>Elástica</b></div>', unsafe_allow_html=True)
                elif abs(Ed) < 1:
                    st.markdown('<div class="warning-box"><b>Inelástica</b></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="success-box"><b>Unitaria</b></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# MÓDULO 3 — Precio Máximo
# ══════════════════════════════════════════════════════
with tabs[2]:
    col_g3, col_r3 = st.columns([2.5, 1])
    with col_r3:
        st.markdown('<div class="section-title">Controles</div>', unsafe_allow_html=True)
        P_max = st.slider("P máx", min_value=0.0,
                          max_value=float(P_eq * 2), value=float(P_eq * 0.7),
                          step=float(P_eq / 100))

    Qd_max = max(0, a - b * P_max)
    Qo_max = max(0, c + d * P_max)
    escasez = max(0, Qd_max - Qo_max)
    es_obligatorio = P_max < P_eq

    with col_g3:
        fig3 = fig_base("Precio Máximo")
        Q_max_plot = max(Qd_vals.max(), Qo_vals.max()) * 1.05
        fig3.add_trace(go.Scatter(
            x=[0, Q_max_plot], y=[P_max, P_max],
            name=f"Máx",
            line=dict(color=COLORS["interv"], width=2.5, dash="dash")
        ))
        if es_obligatorio and escasez > 0:
            fig3.add_vrect(x0=Qo_max, x1=Qd_max,
                           fillcolor=COLORS["shade_escasez"], line_width=0)
            fig3.add_trace(go.Scatter(
                x=[Qo_max, Qd_max], y=[P_max, P_max],
                mode="markers",
                marker=dict(size=10, color=COLORS["interv"]),
                showlegend=False
            ))
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False, "responsive": True})
    
    with col_r3:
        card_grid([
            ("P*", f"${P_eq:.2f}", ""),
            ("P máx", f"${P_max:.2f}", "red" if es_obligatorio else ""),
            ("Qd", f"{Qd_max:.0f}", ""),
            ("Qo", f"{Qo_max:.0f}", ""),
        ])
        if es_obligatorio and escasez > 0:
            card_grid([("Escasez", f"{escasez:.0f}", "red")])

# ══════════════════════════════════════════════════════
# MÓDULO 4 — Precio Mínimo
# ══════════════════════════════════════════════════════
with tabs[3]:
    col_g4, col_r4 = st.columns([2.5, 1])
    with col_r4:
        st.markdown('<div class="section-title">Controles</div>', unsafe_allow_html=True)
        P_min = st.slider("P mín", min_value=0.0,
                          max_value=float(P_eq * 2), value=float(P_eq * 1.4),
                          step=float(P_eq / 100))

    Qd_min = max(0, a - b * P_min)
    Qo_min = max(0, c + d * P_min)
    excedente = max(0, Qo_min - Qd_min)
    es_obligatorio_min = P_min > P_eq

    with col_g4:
        fig4 = fig_base("Precio Mínimo")
        Q_max_plot4 = max(Qd_vals.max(), Qo_vals.max()) * 1.05
        fig4.add_trace(go.Scatter(
            x=[0, Q_max_plot4], y=[P_min, P_min],
            name=f"Mín",
            line=dict(color=COLORS["oferta"], width=2.5, dash="dash")
        ))
        if es_obligatorio_min and excedente > 0:
            fig4.add_vrect(x0=Qd_min, x1=Qo_min,
                           fillcolor=COLORS["shade_excedente"], line_width=0)
            fig4.add_trace(go.Scatter(
                x=[Qd_min, Qo_min], y=[P_min, P_min],
                mode="markers",
                marker=dict(size=10, color=COLORS["oferta"]),
                showlegend=False
            ))
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False, "responsive": True})
    
    with col_r4:
        card_grid([
            ("P*", f"${P_eq:.2f}", ""),
            ("P mín", f"${P_min:.2f}", "green" if es_obligatorio_min else ""),
            ("Qd", f"{Qd_min:.0f}", ""),
            ("Qo", f"{Qo_min:.0f}", ""),
        ])
        if es_obligatorio_min and excedente > 0:
            card_grid([("Excedente", f"{excedente:.0f}", "green")])

# ══════════════════════════════════════════════════════
# MÓDULO 5 — Impuestos
# ══════════════════════════════════════════════════════
with tabs[4]:
    col_g5, col_r5 = st.columns([2.5, 1])
    with col_r5:
        st.markdown('<div class="section-title">Controles</div>', unsafe_allow_html=True)
        tipo_imp = st.radio("Impuesto a:", ["Vendedores", "Compradores"])
        t = st.slider("Monto ($)", min_value=0.0,
                      max_value=float(P_eq * 0.8), value=float(P_eq * 0.12),
                      step=float(P_eq / 200))

    if tipo_imp == "Vendedores":
        c_new = c - d * t
        P_new, Q_new = equilibrio(a, b, c_new, d)
        if P_new is None or Q_new < 0:
            st.error("Parámetros inválidos.")
            st.stop()
        P_comp = P_new
        P_vend = P_new - t
        Qo_new_vals = c_new + d * precios
        Qo_new_vals = np.clip(Qo_new_vals, 0, None)
        label_curva = "Oferta con impuesto"
        curva_nueva_x = Qo_new_vals
        curva_nueva_color = COLORS["interv"]
    else:
        a_new = a - b * t
        P_new, Q_new = equilibrio(a_new, b, c, d)
        if P_new is None or Q_new < 0:
            st.error("Con ese impuesto no hay equilibrio válido.")
            st.stop()
        P_comp = P_new + t
        P_vend = P_new
        Qd_new_vals = a_new - b * precios
        Qd_new_vals = np.clip(Qd_new_vals, 0, None)
        label_curva = "Demanda con impuesto"
        curva_nueva_x = Qd_new_vals
        curva_nueva_color = "#7b1fa2"

    recaudacion = t * Q_new
    inc_comp = (P_comp - P_eq) * Q_new
    inc_vend = (P_eq - P_vend) * Q_new

    with col_g5:
        fig5 = fig_base("Impuestos")
        fig5.add_trace(go.Scatter(x=curva_nueva_x, y=precios, name=label_curva,
                                  line=dict(color=curva_nueva_color, width=2, dash="dash")))
        fig5.add_trace(go.Scatter(x=[Q_new], y=[P_new],
                                  mode="markers", marker=dict(size=11, color=COLORS["interv"], symbol="x"),
                                  showlegend=False))
        if Q_new > 0:
            fig5.add_hline(y=P_comp, line_dash="dot", line_color="goldenrod")
            fig5.add_hline(y=P_vend, line_dash="dot", line_color="#1565c0")
        st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False, "responsive": True})
    
    with col_r5:
        card_grid([
            ("P*", f"${P_eq:.2f}", ""),
            ("P_c", f"${P_comp:.2f}", ""),
            ("P_v", f"${P_vend:.2f}", ""),
            ("Q'", f"{Q_new:.0f}", "red"),
            ("Recaud.", f"${recaudacion:,.0f}", "purple"),
        ])

# ══════════════════════════════════════════════════════
# MÓDULO 6 — Subsidios
# ══════════════════════════════════════════════════════
with tabs[5]:
    col_g6, col_r6 = st.columns([2.5, 1])
    with col_r6:
        st.markdown('<div class="section-title">Controles</div>', unsafe_allow_html=True)
        tipo_sub = st.radio("Subsidio a:", ["Productores", "Compradores"])
        s_pct = st.slider("Subsidio (%)", min_value=0, max_value=80, value=10, step=1)

    s = s_pct / 100
    if tipo_sub == "Productores":
        d_new = d * (1 + s)
        P_new_s, Q_new_s = equilibrio(a, b, c, d_new)
        if P_new_s is None:
            st.error("Sin equilibrio.")
            st.stop()
        Pc = P_new_s
        Ps = P_new_s * (1 + s)
        Qo_sub_vals = c + d_new * precios
        Qo_sub_vals = np.clip(Qo_sub_vals, 0, None)
        costo_gobierno = (Ps - Pc) * Q_new_s
        ganancia_prod = (Ps - P_eq) * Q_new_s
        ganancia_comp = (P_eq - Pc) * Q_new_s if Pc < P_eq else 0
        curva_x = Qo_sub_vals
        curva_label = "Oferta + subsidio"
    else:
        a_new_s = a + b * s * P_eq
        P_new_s, Q_new_s = equilibrio(a_new_s, b, c, d)
        if P_new_s is None:
            st.error("Sin equilibrio.")
            st.stop()
        Pc = P_new_s - s * P_eq
        Ps = P_new_s
        Qd_sub_vals = a_new_s - b * precios
        Qd_sub_vals = np.clip(Qd_sub_vals, 0, None)
        costo_gobierno = (Ps - Pc) * Q_new_s
        ganancia_prod = (Ps - P_eq) * Q_new_s if Ps > P_eq else 0
        ganancia_comp = (P_eq - Pc) * Q_new_s if Pc < P_eq else 0
        curva_x = Qd_sub_vals
        curva_label = "Demanda + subsidio"

    with col_g6:
        fig6 = fig_base("Subsidios")
        fig6.add_trace(go.Scatter(x=curva_x, y=precios, name=curva_label,
                                  line=dict(color=COLORS["subsidio"], width=2, dash="dash")))
        fig6.add_trace(go.Scatter(x=[Q_new_s], y=[P_new_s],
                                  mode="markers", marker=dict(size=11, color=COLORS["subsidio"], symbol="star"),
                                  showlegend=False))
        fig6.add_hline(y=Ps, line_dash="dot", line_color=COLORS["subsidio"])
        fig6.add_hline(y=Pc, line_dash="dot", line_color=COLORS["demanda"])
        st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False, "responsive": True})
    
    with col_r6:
        card_grid([
            ("P*", f"${P_eq:.2f}", ""),
            ("Pc", f"${Pc:.2f}", "green"),
            ("Ps", f"${Ps:.2f}", "purple"),
            ("Q'", f"{Q_new_s:.0f}", ""),
            ("Costo gob.", f"${costo_gobierno:,.0f}", "red"),
        ])

# ══════════════════════════════════════════════════════
# MÓDULO 7 — Cuotas
# ══════════════════════════════════════════════════════
with tabs[6]:
    col_g7, col_r7 = st.columns([2.5, 1])
    with col_r7:
        st.markdown('<div class="section-title">Controles</div>', unsafe_allow_html=True)
        Q_max_posible = float(Q_eq * 1.5)
        Q_cuota = st.slider("Cuota", min_value=1.0,
                            max_value=Q_max_posible, value=float(Q_eq * 0.75),
                            step=1.0)

    Pd_cuota = (a - Q_cuota) / b
    Ps_cuota = (Q_cuota - c) / d if d != 0 else 0
    renta = max(0, Pd_cuota - Ps_cuota)

    with col_g7:
        fig7 = fig_base("Cuota")
        fig7.add_vline(x=Q_cuota, line_dash="dash", line_color=COLORS["cuota"], line_width=2.5)
        fig7.add_trace(go.Scatter(
            x=[Q_cuota, Q_cuota], y=[Pd_cuota, Ps_cuota],
            mode="markers",
            marker=dict(size=11, color=[COLORS["demanda"], COLORS["oferta"]]),
            showlegend=False
        ))
        if renta > 0 and Q_cuota > 0:
            fig7.add_shape(type="rect",
                           x0=0, x1=Q_cuota,
                           y0=Ps_cuota, y1=Pd_cuota,
                           fillcolor="rgba(0,131,143,0.2)", line_width=0)
        st.plotly_chart(fig7, use_container_width=True, config={"displayModeBar": False, "responsive": True})
    
    with col_r7:
        card_grid([
            ("P*", f"${P_eq:.2f}", ""),
            ("Q*", f"{Q_eq:.0f}", ""),
            ("Cuota", f"{Q_cuota:.0f}", "purple"),
            ("Pd", f"${Pd_cuota:.2f}", "red"),
            ("Ps", f"${Ps_cuota:.2f}", "green"),
            ("Renta", f"${renta * Q_cuota:,.0f}", "purple"),
        ])
