import streamlit as st
import plotly.graph_objects as go

COLORS = dict(
    demanda="#2196f3", oferta="#4caf50", 
    eq="#ff9800", interv="#f44336", subsidio="#ab47bc",
    cuota="#00bcd4", shade_escasez="rgba(244,67,54,0.15)",
    shade_excedente="rgba(76,175,80,0.15)",
    shade_imp_comp="rgba(255,152,0,0.3)",
    shade_imp_vend="rgba(33,150,243,0.3)",
)

def load_css():
    st.markdown("""
    <style>
        .main-header {
            background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #e65100 100%);
            padding: 20px 30px; border-radius: 12px; margin-bottom: 20px; color: white;
        }
        .main-header h1 { margin: 0; font-size: 2rem; }
        .main-header p  { margin: 4px 0 0; opacity: .85; font-size: 1rem; }

        .metric-card {
            background: var(--background-color);
            border-left: 4px solid #7986cb;
            border-radius: 8px; padding: 14px 18px; margin: 6px 0;
            box-shadow: 0 1px 3px rgba(128,128,128,0.2);
        }
        .metric-card.green  { border-color: #4caf50; }
        .metric-card.orange { border-color: #ff9800; }
        .metric-card.red    { border-color: #ef5350; }
        .metric-card.purple { border-color: #ab47bc; }

        .metric-label { font-size: .78rem; color: inherit; opacity: 0.8; font-weight: 600; text-transform: uppercase; }
        .metric-value { font-size: 1.4rem; font-weight: 700; color: #7986cb; }
        .metric-card.green  .metric-value { color: #4caf50; }
        .metric-card.orange .metric-value { color: #ff9800; }
        .metric-card.red    .metric-value { color: #ef5350; }
        .metric-card.purple .metric-value { color: #ab47bc; }

        .info-box { background: rgba(121, 134, 203, 0.1); border-left: 3px solid #7986cb; border-radius: 8px; padding: 14px; margin: 10px 0;}
        .section-title { font-size: 1.1rem; font-weight: 700; color: #7986cb; border-bottom: 2px solid #e65100; padding-bottom: 6px; margin: 18px 0 12px;}
    </style>
    """, unsafe_allow_html=True)

def card(label, value, color=""):
    st.markdown(f'<div class="metric-card {color}"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

def fig_base(title, Qd_vals, Qo_vals, precios, Q_eq, P_eq):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=Qd_vals, y=precios, name="Demanda", line=dict(color=COLORS["demanda"], width=2.5)))
    fig.add_trace(go.Scatter(x=Qo_vals, y=precios, name="Oferta", line=dict(color=COLORS["oferta"], width=2.5)))
    fig.add_trace(go.Scatter(x=[Q_eq], y=[P_eq], name=f"Equilibrio (P={P_eq:.2f}, Q={Q_eq:.0f})", mode="markers", marker=dict(color=COLORS["eq"], size=12)))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="#7986cb")),
        xaxis_title="Cantidad", yaxis_title="Precio",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=480, margin=dict(l=60, r=30, t=60, b=50),
    )
    fig.update_xaxes(gridcolor="rgba(128,128,128,0.2)", zeroline=True, zerolinecolor="rgba(128,128,128,0.5)")
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.2)", zeroline=True, zerolinecolor="rgba(128,128,128,0.5)")
    return fig