import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="Simulador de Mercado - UNSTA",
    page_icon="📈",
    layout="wide"
)

# ─── Estilos ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #e65100 100%);
        padding: 20px 30px;
        border-radius: 12px;
        margin-bottom: 20px;
        color: white;
    }
    .main-header h1 { margin: 0; font-size: 2rem; }
    .main-header p  { margin: 4px 0 0; opacity: .85; font-size: 1rem; }

    .metric-card {
        background: #f8f9fa;
        border-left: 4px solid #1a237e;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 6px 0;
    }
    .metric-card.green  { border-color: #2e7d32; }
    .metric-card.orange { border-color: #e65100; }
    .metric-card.red    { border-color: #c62828; }
    .metric-card.purple { border-color: #6a1b9a; }

    .metric-label { font-size: .78rem; color: #666; font-weight: 600;
                    text-transform: uppercase; letter-spacing: .5px; }
    .metric-value { font-size: 1.4rem; font-weight: 700; color: #1a237e; }
    .metric-card.green  .metric-value { color: #2e7d32; }
    .metric-card.orange .metric-value { color: #e65100; }
    .metric-card.red    .metric-value { color: #c62828; }
    .metric-card.purple .metric-value { color: #6a1b9a; }

    .info-box {
        background: #e8eaf6;
        border-radius: 8px;
        padding: 14px 16px;
        margin: 10px 0;
        font-size: .9rem;
        color: #1a237e;
    }
    .warning-box {
        background: #fff3e0;
        border-radius: 8px;
        padding: 14px 16px;
        margin: 10px 0;
        font-size: .9rem;
        color: #bf360c;
    }
    .success-box {
        background: #e8f5e9;
        border-radius: 8px;
        padding: 14px 16px;
        margin: 10px 0;
        font-size: .9rem;
        color: #1b5e20;
    }
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1a237e;
        border-bottom: 2px solid #e65100;
        padding-bottom: 6px;
        margin: 18px 0 12px;
    }
    div[data-testid="stTabs"] button { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ─── Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>📈 Simulador de Mercado — Economía para Ingenieros</h1>
  <p>Facultad de Ingeniería · UNSTA · Prof. Raúl García</p>
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
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'</div>', unsafe_allow_html=True
    )

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
with st.sidebar:
    st.markdown("## ⚙️ Configurar Mercado")
    metodo = st.radio("Método de ingreso", ["Forma algebraica", "Desde dos puntos"], key="metodo")
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
        with col1:
            dp1p = st.number_input("P₁ (dem)", value=10.0)
            dp2p = st.number_input("P₂ (dem)", value=30.0)
        with col2:
            dp1q = st.number_input("Q₁ (dem)", value=700.0)
            dp2q = st.number_input("Q₂ (dem)", value=100.0)

        st.markdown("**Oferta — dos puntos**")
        col3, col4 = st.columns(2)
        with col3:
            op1p = st.number_input("P₁ (ofe)", value=5.0)
            op2p = st.number_input("P₂ (ofe)", value=25.0)
        with col4:
            op1q = st.number_input("Q₁ (ofe)", value=100.0)
            op2q = st.number_input("Q₂ (ofe)", value=500.0)

        a_raw, b_raw = construir_desde_puntos(dp1p, dp1q, dp2p, dp2q, "demanda")
        c_raw, d_raw = construir_desde_puntos(op1p, op1q, op2p, op2q, "oferta")

        if a_raw is None or b_raw is None or c_raw is None or d_raw is None:
            st.error("Los puntos ingresados generan una curva vertical (P₁ = P₂). Revisá los datos.")
            valid = False
            a = b = c = d = 1.0
        else:
            a, b, c, d = a_raw, b_raw, c_raw, d_raw
            valid = True
            st.info(f"Demanda deducida: Qd = {a:.2f} − {b:.2f}·P\n\nOferta deducida: Qo = {c:.2f} + {d:.2f}·P")

    st.markdown("---")
    st.caption("Ingeniería Informática — UNSTA")

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
        title=dict(text=title, font=dict(size=16, color="#1a237e")),
        xaxis_title="Cantidad", yaxis_title="Precio",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="#fafafa", paper_bgcolor="white",
        height=480,
        margin=dict(l=60, r=30, t=60, b=50),
    )
    fig.update_xaxes(gridcolor="#eeeeee", zeroline=True, zerolinecolor="#bbb")
    fig.update_yaxes(gridcolor="#eeeeee", zeroline=True, zerolinecolor="#bbb")
    return fig

# ═══════════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "📊 Módulo 1: Mercado",
    "📐 Módulo 2: Elasticidad",
    "🔴 Precio Máximo",
    "🟢 Precio Mínimo",
    "💰 Impuestos",
    "🎁 Subsidios",
    "📦 Cuotas",
])

# ══════════════════════════════════════════════════════
# TAB 1 — Mercado competitivo
# ══════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("### 📊 Mercado Competitivo")
    col_g, col_r = st.columns([2, 1])

    with col_g:
        fig = fig_base("Equilibrio de Mercado")
        # Líneas punteadas al equilibrio
        fig.add_shape(type="line", x0=0, y0=P_eq, x1=Q_eq, y1=P_eq,
                      line=dict(dash="dot", color=COLORS["eq"], width=1.5))
        fig.add_shape(type="line", x0=Q_eq, y0=0, x1=Q_eq, y1=P_eq,
                      line=dict(dash="dot", color=COLORS["eq"], width=1.5))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown('<div class="section-title">Funciones</div>', unsafe_allow_html=True)
        st.markdown(f"**Demanda:** Qd = {a:.2f} − {b:.2f}·P")
        st.markdown(f"**Oferta:** &nbsp;&nbsp;Qo = {c:.2f} + {d:.2f}·P")

        st.markdown('<div class="section-title">Equilibrio</div>', unsafe_allow_html=True)
        card("Precio de equilibrio P*", f"${P_eq:.4f}", "orange")
        card("Cantidad de equilibrio Q*", f"{Q_eq:.2f} unidades")

        st.markdown('<div class="section-title">Derivación analítica</div>', unsafe_allow_html=True)
        st.markdown(f"""
        Igualando Qd = Qo:

        `{a:.2f} − {b:.2f}·P = {c:.2f} + {d:.2f}·P`

        `{a-c:.2f} = {b+d:.2f}·P`

        **P* = {P_eq:.4f}**

        Q* = {c:.2f} + {d:.2f} × {P_eq:.4f} = **{Q_eq:.2f}**
        """)

# ══════════════════════════════════════════════════════
# TAB 2 — Elasticidad (método punto medio Mankiw)
# ══════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("### 📐 Elasticidad-Precio de la Demanda")
    st.markdown("""
    **Método del punto medio (Mankiw):**

    $$E_d = \\frac{(Q_2 - Q_1) / [(Q_1 + Q_2)/2]}{(P_2 - P_1) / [(P_1 + P_2)/2]}$$
    """)

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.markdown("**Punto A**")
        P1_e = st.number_input("Precio P₁", value=float(round(P_eq * 0.8, 2)), key="P1e")
        Q1_e = st.number_input("Cantidad Q₁", value=float(round(a - b * P1_e, 2)), key="Q1e")
    with col_e2:
        st.markdown("**Punto B**")
        P2_e = st.number_input("Precio P₂", value=float(round(P_eq * 1.2, 2)), key="P2e")
        Q2_e = st.number_input("Cantidad Q₂", value=float(round(a - b * P2_e, 2)), key="Q2e")

    col_g2, col_r2 = st.columns([2, 1])
    with col_g2:
        fig2 = fig_base("Elasticidad — Puntos seleccionados")
        fig2.add_trace(go.Scatter(
            x=[Q1_e, Q2_e], y=[P1_e, P2_e],
            name="Puntos A y B", mode="markers+text",
            marker=dict(size=13, color="#9c27b0", symbol="diamond"),
            text=["A", "B"], textposition="top right",
            textfont=dict(size=13, color="#9c27b0")
        ))
        st.plotly_chart(fig2, use_container_width=True)

    with col_r2:
        if P2_e == P1_e:
            st.error("P₁ y P₂ no pueden ser iguales.")
        else:
            dQ = Q2_e - Q1_e
            dP = P2_e - P1_e
            Q_med = (Q1_e + Q2_e) / 2
            P_med = (P1_e + P2_e) / 2
            if Q_med == 0 or P_med == 0:
                st.error("Promedio de Q o P es cero. Revisá los puntos.")
            else:
                Ed = (dQ / Q_med) / (dP / P_med)

                st.markdown('<div class="section-title">Resultado</div>', unsafe_allow_html=True)
                card("Elasticidad |Ed|", f"{abs(Ed):.4f}", "purple")

                if abs(Ed) > 1:
                    tipo = "🔵 ELÁSTICA"
                    color_tipo = "info-box"
                    ing = "⬇️ El ingreso total **disminuye** si el precio sube."
                elif abs(Ed) < 1:
                    tipo = "🟠 INELÁSTICA"
                    color_tipo = "warning-box"
                    ing = "⬆️ El ingreso total **aumenta** si el precio sube."
                else:
                    tipo = "🟢 UNITARIA"
                    color_tipo = "success-box"
                    ing = "➡️ El ingreso total **no cambia** ante cambios de precio."

                st.markdown(f'<div class="{color_tipo}"><b>{tipo}</b><br>{ing}</div>', unsafe_allow_html=True)

                IT_A = P1_e * Q1_e
                IT_B = P2_e * Q2_e
                card("Ingreso Total en A", f"${IT_A:,.2f}", "green" if IT_A >= IT_B else "red")
                card("Ingreso Total en B", f"${IT_B:,.2f}", "green" if IT_B >= IT_A else "red")

                st.markdown('<div class="section-title">Cálculo paso a paso</div>', unsafe_allow_html=True)
                st.markdown(f"""
                ΔQ = {dQ:.2f} | Q̄ = {Q_med:.2f}

                ΔP = {dP:.2f} | P̄ = {P_med:.2f}

                Ed = ({dQ:.2f}/{Q_med:.2f}) / ({dP:.2f}/{P_med:.2f})

                **Ed = {Ed:.4f}**
                """)

# ══════════════════════════════════════════════════════
# TAB 3 — Precio Máximo
# ══════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("### 🔴 Precio Máximo (Techo de Precio)")

    col_ctrl, col_info = st.columns([1, 2])
    with col_ctrl:
        P_max = st.slider("Precio Máximo ($)", min_value=0.0,
                          max_value=float(P_eq * 2), value=float(P_eq * 0.7),
                          step=float(P_eq / 100))

    Qd_max = max(0, a - b * P_max)
    Qo_max = max(0, c + d * P_max)
    escasez = max(0, Qd_max - Qo_max)
    es_obligatorio = P_max < P_eq

    col_g3, col_r3 = st.columns([2, 1])
    with col_g3:
        fig3 = fig_base("Precio Máximo")
        # Línea de precio máximo
        Q_max_plot = max(Qd_vals.max(), Qo_vals.max()) * 1.05
        fig3.add_trace(go.Scatter(
            x=[0, Q_max_plot], y=[P_max, P_max],
            name=f"Precio Máximo (${P_max:.2f})",
            line=dict(color=COLORS["interv"], width=2.5, dash="dash")
        ))
        if es_obligatorio and escasez > 0:
            # Área de escasez
            fig3.add_vrect(x0=Qo_max, x1=Qd_max,
                           fillcolor=COLORS["shade_escasez"], line_width=0,
                           annotation_text="Escasez", annotation_position="top right",
                           annotation_font_color=COLORS["interv"])
            fig3.add_trace(go.Scatter(
                x=[Qo_max, Qd_max], y=[P_max, P_max],
                mode="markers",
                marker=dict(size=10, color=COLORS["interv"]),
                name=f"Qo={Qo_max:.0f}  |  Qd={Qd_max:.0f}",
                showlegend=True
            ))
        st.plotly_chart(fig3, use_container_width=True)

    with col_r3:
        if es_obligatorio:
            st.markdown('<div class="warning-box">⚠️ El precio máximo es <b>obligatorio</b> (está por debajo del equilibrio).</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-box">✅ El precio máximo <b>no es obligatorio</b> (está por encima del equilibrio). El mercado opera libremente.</div>', unsafe_allow_html=True)

        card("Precio de equilibrio P*", f"${P_eq:.2f}", "orange")
        card("Precio Máximo", f"${P_max:.2f}", "red")
        card("Cantidad demandada (Qd)", f"{Qd_max:.2f}")
        card("Cantidad ofrecida (Qo)", f"{Qo_max:.2f}")
        if es_obligatorio:
            card("Escasez (Qd − Qo)", f"{escasez:.2f}", "red")
            st.markdown("""
            <div class="info-box">
            <b>¿Qué ocurre?</b><br>
            Los compradores quieren más de lo que los vendedores están dispuestos a ofrecer.
            Surge la <b>escasez</b>. Puede aparecer: colas, mercado negro, racionamiento.
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# TAB 4 — Precio Mínimo
# ══════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("### 🟢 Precio Mínimo (Piso de Precio)")

    P_min = st.slider("Precio Mínimo ($)", min_value=0.0,
                      max_value=float(P_eq * 2), value=float(P_eq * 1.4),
                      step=float(P_eq / 100))

    Qd_min = max(0, a - b * P_min)
    Qo_min = max(0, c + d * P_min)
    excedente = max(0, Qo_min - Qd_min)
    es_obligatorio_min = P_min > P_eq

    col_g4, col_r4 = st.columns([2, 1])
    with col_g4:
        fig4 = fig_base("Precio Mínimo")
        Q_max_plot4 = max(Qd_vals.max(), Qo_vals.max()) * 1.05
        fig4.add_trace(go.Scatter(
            x=[0, Q_max_plot4], y=[P_min, P_min],
            name=f"Precio Mínimo (${P_min:.2f})",
            line=dict(color=COLORS["oferta"], width=2.5, dash="dash")
        ))
        if es_obligatorio_min and excedente > 0:
            fig4.add_vrect(x0=Qd_min, x1=Qo_min,
                           fillcolor=COLORS["shade_excedente"], line_width=0,
                           annotation_text="Excedente", annotation_position="top right",
                           annotation_font_color=COLORS["oferta"])
            fig4.add_trace(go.Scatter(
                x=[Qd_min, Qo_min], y=[P_min, P_min],
                mode="markers",
                marker=dict(size=10, color=COLORS["oferta"]),
                name=f"Qd={Qd_min:.0f}  |  Qo={Qo_min:.0f}"
            ))
        st.plotly_chart(fig4, use_container_width=True)

    with col_r4:
        if es_obligatorio_min:
            st.markdown('<div class="warning-box">⚠️ El precio mínimo es <b>obligatorio</b> (está por encima del equilibrio).</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-box">✅ El precio mínimo <b>no es obligatorio</b>. El mercado opera al precio de equilibrio.</div>', unsafe_allow_html=True)

        card("Precio de equilibrio P*", f"${P_eq:.2f}", "orange")
        card("Precio Mínimo", f"${P_min:.2f}", "green")
        card("Cantidad demandada (Qd)", f"{Qd_min:.2f}")
        card("Cantidad ofrecida (Qo)", f"{Qo_min:.2f}")
        if es_obligatorio_min:
            card("Excedente (Qo − Qd)", f"{excedente:.2f}", "green")
            st.markdown("""
            <div class="info-box">
            <b>¿Qué ocurre?</b><br>
            Los vendedores quieren vender más de lo que los compradores demandan.
            Surge el <b>excedente</b>. Ejemplo clásico: salario mínimo → desempleo.
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# TAB 5 — Impuestos
# ══════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("### 💰 Impuestos e Incidencia Fiscal")

    col_ti1, col_ti2 = st.columns(2)
    with col_ti1:
        tipo_imp = st.radio("Impuesto aplicado a:", ["Vendedores (desplaza Oferta ↑)", "Compradores (desplaza Demanda ↓)"])
    with col_ti2:
        t = st.slider("Monto del impuesto por unidad ($)", min_value=0.0,
                      max_value=float(P_eq * 0.8), value=float(P_eq * 0.12),
                      step=float(P_eq / 200))

    if "Vendedores" in tipo_imp:
        # Oferta se desplaza arriba: nueva Qo' = c - d*t + d*P  =>  c' = c - d*t
        c_new = c - d * t
        P_new, Q_new = equilibrio(a, b, c_new, d)
        if P_new is None or Q_new < 0:
            st.error("Con ese impuesto no hay equilibrio válido.")
            st.stop()
        P_comp = P_new          # precio que pagan compradores
        P_vend = P_new - t      # precio que reciben vendedores
        Qo_new_vals = c_new + d * precios
        Qo_new_vals = np.clip(Qo_new_vals, 0, None)
        label_curva = "Oferta con impuesto"
        curva_nueva_x = Qo_new_vals
        curva_nueva_color = COLORS["interv"]
    else:
        # Demanda se desplaza abajo: nueva Qd' = a - b*t - b*P  =>  a' = a - b*t
        a_new = a - b * t
        P_new, Q_new = equilibrio(a_new, b, c, d)
        if P_new is None or Q_new < 0:
            st.error("Con ese impuesto no hay equilibrio válido.")
            st.stop()
        P_comp = P_new + t      # precio que pagan compradores (incluye impuesto)
        P_vend = P_new          # precio que reciben vendedores
        Qd_new_vals = a_new - b * precios
        Qd_new_vals = np.clip(Qd_new_vals, 0, None)
        label_curva = "Demanda con impuesto"
        curva_nueva_x = Qd_new_vals
        curva_nueva_color = "#7b1fa2"

    recaudacion = t * Q_new
    inc_comp = (P_comp - P_eq) * Q_new
    inc_vend = (P_eq - P_vend) * Q_new

    col_g5, col_r5 = st.columns([2, 1])
    with col_g5:
        fig5 = fig_base("Impuestos — Incidencia Fiscal")
        # Curva desplazada
        if "Vendedores" in tipo_imp:
            fig5.add_trace(go.Scatter(x=curva_nueva_x, y=precios, name=label_curva,
                                      line=dict(color=curva_nueva_color, width=2, dash="dash")))
        else:
            fig5.add_trace(go.Scatter(x=curva_nueva_x, y=precios, name=label_curva,
                                      line=dict(color=curva_nueva_color, width=2, dash="dash")))

        # Nuevo equilibrio
        fig5.add_trace(go.Scatter(x=[Q_new], y=[P_new],
                                  name=f"Nuevo equil. (${P_new:.2f}, {Q_new:.0f})",
                                  mode="markers", marker=dict(size=12, color=COLORS["interv"], symbol="x")))

        # Área pago compradores (amarillo) y vendedores (azul)
        if Q_new > 0:
            fig5.add_shape(type="rect",
                           x0=0, x1=Q_new, y0=P_eq, y1=P_comp,
                           fillcolor=COLORS["shade_imp_comp"], line_width=0)
            fig5.add_shape(type="rect",
                           x0=0, x1=Q_new, y0=P_vend, y1=P_eq,
                           fillcolor=COLORS["shade_imp_vend"], line_width=0)
            # Líneas P_comp y P_vend
            fig5.add_hline(y=P_comp, line_dash="dot", line_color="goldenrod",
                           annotation_text=f"P compradores ${P_comp:.2f}", annotation_position="right")
            fig5.add_hline(y=P_vend, line_dash="dot", line_color="#1565c0",
                           annotation_text=f"P vendedores ${P_vend:.2f}", annotation_position="right")

        st.plotly_chart(fig5, use_container_width=True)

    with col_r5:
        card("Precio equilibrio original", f"${P_eq:.2f}", "orange")
        card("Nueva cantidad Q'", f"{Q_new:.2f}", "red")
        card("Precio que pagan compradores", f"${P_comp:.2f}", "orange")
        card("Precio que reciben vendedores", f"${P_vend:.2f}", "green")
        card("Recaudación total", f"${recaudacion:,.2f}", "purple")
        card("Paga el comprador", f"${inc_comp:,.2f}", "orange")
        card("Paga el vendedor", f"${inc_vend:,.2f}", "green")

        st.markdown("""
        <div class="info-box">
        <b>Incidencia fiscal</b><br>
        La carga del impuesto se distribuye según la
        <b>elasticidad relativa</b>. Quien tiene la curva más
        <i>inelástica</i> soporta mayor parte del impuesto,
        independientemente de sobre quién se aplique legalmente.
        </div>
        """, unsafe_allow_html=True)

        if inc_comp + inc_vend > 0:
            pct_comp = inc_comp / (inc_comp + inc_vend) * 100
            pct_vend = inc_vend / (inc_comp + inc_vend) * 100
            card(f"% que absorbe el comprador", f"{pct_comp:.1f}%", "orange")
            card(f"% que absorbe el vendedor", f"{pct_vend:.1f}%", "green")

# ══════════════════════════════════════════════════════
# TAB 6 — Subsidios
# ══════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("### 🎁 Subsidios")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        tipo_sub = st.radio("Subsidio aplicado a:", ["Productores (s% sobre precio)", "Compradores (descuento precio)"])
    with col_s2:
        s_pct = st.slider("Subsidio (%)", min_value=0, max_value=80, value=10, step=1)

    # Subsidio a productores: nueva oferta se desplaza abajo
    # Ps = Pd * (1+s) => Qo = 2.86 * Pd*(1+s)  => c_new=c, d_new=d*(1+s/100)
    s = s_pct / 100

    if "Productores" in tipo_sub:
        d_new = d * (1 + s)
        P_new_s, Q_new_s = equilibrio(a, b, c, d_new)
        if P_new_s is None:
            st.error("Sin equilibrio.")
            st.stop()
        Pc = P_new_s               # precio que pagan compradores
        Ps = P_new_s * (1 + s)    # precio que reciben productores
        Qo_sub_vals = c + d_new * precios
        Qo_sub_vals = np.clip(Qo_sub_vals, 0, None)
        costo_gobierno = (Ps - Pc) * Q_new_s
        ganancia_prod = (Ps - P_eq) * Q_new_s
        ganancia_comp = (P_eq - Pc) * Q_new_s if Pc < P_eq else 0
    else:
        # Subsidio a compradores: demanda se desplaza arriba
        a_new_s = a + b * s * P_eq   # simplificado: comprador recibe s% del precio eq
        P_new_s, Q_new_s = equilibrio(a_new_s, b, c, d)
        if P_new_s is None:
            st.error("Sin equilibrio.")
            st.stop()
        Pc = P_new_s - s * P_eq   # precio efectivo para comprador
        Ps = P_new_s
        Qd_sub_vals = a_new_s - b * precios
        Qd_sub_vals = np.clip(Qd_sub_vals, 0, None)
        costo_gobierno = (Ps - Pc) * Q_new_s
        ganancia_prod = (Ps - P_eq) * Q_new_s if Ps > P_eq else 0
        ganancia_comp = (P_eq - Pc) * Q_new_s if Pc < P_eq else 0

    col_g6, col_r6 = st.columns([2, 1])
    with col_g6:
        fig6 = fig_base("Subsidios — Efecto sobre el Mercado")
        if "Productores" in tipo_sub:
            fig6.add_trace(go.Scatter(x=Qo_sub_vals, y=precios, name="Oferta con subsidio",
                                      line=dict(color=COLORS["subsidio"], width=2, dash="dash")))
        else:
            fig6.add_trace(go.Scatter(x=Qd_sub_vals, y=precios, name="Demanda con subsidio",
                                      line=dict(color=COLORS["subsidio"], width=2, dash="dash")))

        fig6.add_trace(go.Scatter(x=[Q_new_s], y=[P_new_s],
                                  name=f"Nuevo equil. (${P_new_s:.2f}, {Q_new_s:.0f})",
                                  mode="markers", marker=dict(size=12, color=COLORS["subsidio"], symbol="star")))
        fig6.add_hline(y=Ps, line_dash="dot", line_color=COLORS["subsidio"],
                       annotation_text=f"P productores ${Ps:.2f}")
        fig6.add_hline(y=Pc, line_dash="dot", line_color=COLORS["demanda"],
                       annotation_text=f"P compradores ${Pc:.2f}")
        st.plotly_chart(fig6, use_container_width=True)

    with col_r6:
        card("Precio equilibrio original", f"${P_eq:.2f}", "orange")
        card("Nueva cantidad Q'", f"{Q_new_s:.2f}")
        card("Precio que pagan compradores", f"${Pc:.2f}", "green")
        card("Precio que reciben productores", f"${Ps:.2f}", "purple")
        card("Costo del gobierno", f"${costo_gobierno:,.2f}", "red")
        card("Ganancia productores", f"${ganancia_prod:,.2f}", "green")
        card("Ganancia compradores", f"${ganancia_comp:,.2f}", "green")

        st.markdown("""
        <div class="info-box">
        <b>Bienestar social:</b><br>
        El subsidio genera un costo al gobierno mayor que
        la suma de ganancias de productores y consumidores.
        La diferencia es la <b>pérdida irrecuperable de eficiencia</b> (triángulo ABC).
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# TAB 7 — Cuotas
# ══════════════════════════════════════════════════════
with tabs[6]:
    st.markdown("### 📦 Cuota de Producción")

    Q_max_posible = float(Q_eq * 1.5)
    Q_cuota = st.slider("Cuota de producción (máximo permitido)", min_value=1.0,
                        max_value=Q_max_posible, value=float(Q_eq * 0.75),
                        step=1.0)

    # Con cuota Xc: Qo = Xc fijo
    # Pd: precio que pagan compradores = (a - Xc) / b
    # Ps: precio al que quieren vender productores = (Xc - c) / d
    Pd_cuota = (a - Q_cuota) / b   # precio demanda a esa cantidad
    Ps_cuota = (Q_cuota - c) / d if d != 0 else 0   # precio oferta a esa cantidad
    renta = max(0, Pd_cuota - Ps_cuota)

    col_g7, col_r7 = st.columns([2, 1])
    with col_g7:
        fig7 = fig_base("Cuota de Producción")
        # Línea vertical de cuota
        fig7.add_vline(x=Q_cuota, line_dash="dash", line_color=COLORS["cuota"], line_width=2.5,
                       annotation_text=f"Cuota = {Q_cuota:.0f}", annotation_position="top right",
                       annotation_font_color=COLORS["cuota"])
        # Puntos Pd y Ps
        fig7.add_trace(go.Scatter(
            x=[Q_cuota, Q_cuota], y=[Pd_cuota, Ps_cuota],
            mode="markers+text",
            marker=dict(size=12, color=[COLORS["demanda"], COLORS["oferta"]]),
            text=[f"Pd=${Pd_cuota:.2f}", f"Ps=${Ps_cuota:.2f}"],
            textposition=["top right", "bottom right"],
            name="Precios con cuota"
        ))
        # Área de renta
        if renta > 0 and Q_cuota > 0:
            fig7.add_shape(type="rect",
                           x0=0, x1=Q_cuota,
                           y0=Ps_cuota, y1=Pd_cuota,
                           fillcolor="rgba(0,131,143,0.2)", line_width=0)
        st.plotly_chart(fig7, use_container_width=True)

    with col_r7:
        card("Precio equilibrio P*", f"${P_eq:.2f}", "orange")
        card("Cantidad equilibrio Q*", f"{Q_eq:.2f}")
        card("Cuota impuesta", f"{Q_cuota:.0f} unidades", "purple")
        card("Precio pagan compradores (Pd)", f"${Pd_cuota:.2f}", "red")
        card("Costo producción (Ps)", f"${Ps_cuota:.2f}", "green")
        card("Renta por unidad (Pd − Ps)", f"${renta:.2f}", "purple")
        card("Renta total", f"${renta * Q_cuota:,.2f}", "purple")

        if Q_cuota < Q_eq:
            st.markdown("""
            <div class="warning-box">
            <b>Cuota obligatoria:</b> La cuota está por debajo del
            equilibrio. Los productores obtienen una <b>renta</b>
            (Pd − Ps) por cada unidad. La sociedad pierde bienestar
            (triángulo de pérdida irrecuperable).
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="success-box">
            ✅ La cuota está <b>por encima o igual al equilibrio</b>.
            El mercado opera libremente al precio P*.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class="info-box">
        <b>¿Quién gana y quién pierde?</b><br>
        • <b>Gobierno:</b> no recauda ni paga nada.<br>
        • <b>Productores:</b> pueden ganar o perder según la renta.<br>
        • <b>Consumidores:</b> siempre pierden (pagan Pd > P*).<br>
        • <b>Sociedad:</b> pierde eficiencia (triángulo ABC).
        </div>
        """, unsafe_allow_html=True)
