import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Rendimiento - Google Search Console", layout="wide", page_icon="📈")

# --- CSS PARA REPLICAR LA ESTÉTICA GSC ---
st.markdown("""
    <style>
    .main { background-color: #f1f3f4; }
    /* Tarjetas de Métricas */
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px 8px 0 0;
        border-bottom: 4px solid #4285f4;
        text-align: left;
    }
    .metric-label { font-size: 14px; color: #5f6368; display: flex; align-items: center; }
    .metric-value { font-size: 24px; font-weight: 500; color: #202124; margin-top: 5px; }
    
    /* Contenedores de Tablas y Gráficos */
    .gsc-container {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #dadce0;
        margin-bottom: 20px;
    }
    
    /* Tabs personalizadas */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; background-color: white; border-bottom: 1px solid #dadce0; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; font-weight: 500; color: #5f6368; }
    .stTabs [aria-selected="true"] { color: #1a73e8; border-bottom-color: #1a73e8; }
    </style>
    """, unsafe_allow_html=True)

# --- GENERACIÓN DE DATOS SIMULADOS ---
def get_mock_data():
    dates = pd.date_range(start="2025-10-19", end="2026-01-17")
    queries = ["creactive hub", "creative hub", "creactive hub agencia", "creactivity hub", "creactive", "creactivityhub"]
    
    data = []
    for date in dates:
        for q in queries:
            c = np.random.randint(0, 5)
            i = np.random.randint(20, 100)
            data.append([date, q, c, i, np.random.uniform(4, 10)])
    
    df = pd.DataFrame(data, columns=['Fecha', 'Query', 'Clicks', 'Impresiones', 'Posicion'])
    return df

df = get_mock_data()

# --- HEADER TIPO GSC ---
st.title("Rendimiento")
st.caption("Tipo de búsqueda: Web | Fecha: Últimos 3 meses")

# --- TARJETAS DE MÉTRICAS (SUPERIORES) ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f'<div class="metric-card" style="border-bottom-color: #4285f4;"><div class="metric-label">☑ Clics totales</div><div class="metric-value">{df["Clicks"].sum()}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card" style="border-bottom-color: #7e3ff2;"><div class="metric-label">☑ Impresiones totales</div><div class="metric-value">{(df["Impresiones"].sum()/1000):.1f} mil</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card" style="border-bottom-color: #00897b; opacity: 0.5;"><div class="metric-label">☐ CTR medio</div><div class="metric-value">7,5 %</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card" style="border-bottom-color: #e8710a; opacity: 0.5;"><div class="metric-label">☐ Posición media</div><div class="metric-value">6,9</div></div>', unsafe_allow_html=True)

# --- GRÁFICO DE RENDIMIENTO ---
st.markdown('<div class="gsc-container">', unsafe_allow_html=True)
trend = df.groupby('Fecha').agg({'Clicks':'sum', 'Impresiones':'sum'}).reset_index()

fig = go.Figure()
fig.add_trace(go.Scatter(x=trend['Fecha'], y=trend['Clicks'], name="Clics", line=dict(color='#4285f4', width=2)))
fig.add_trace(go.Scatter(x=trend['Fecha'], y=trend['Impresiones'], name="Impresiones", line=dict(color='#7e3ff2', width=2), yaxis="y2"))

fig.update_layout(
    yaxis=dict(title="Clics", titlefont=dict(color="#4285f4"), tickfont=dict(color="#4285f4")),
    yaxis2=dict(title="Impresiones", titlefont=dict(color="#7e3ff2"), tickfont=dict(color="#7e3ff2"), overlaying="y", side="right"),
    hovermode="x unified",
    margin=dict(l=0, r=0, t=20, b=0),
    plot_bgcolor='white',
    height=400,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- TABS INFERIORES ---
st.markdown('<div class="gsc-container">', unsafe_allow_html=True)
tab1, tab2, tab3, tab4 = st.tabs(["CONSULTAS", "PÁGINAS", "PAÍSES", "DISPOSITIVOS"])

with tab1:
    # Tabla de consultas similar a la imagen
    q_df = df.groupby('Query').agg({'Clicks':'sum', 'Impresiones':'sum'}).reset_index().sort_values('Clicks', ascending=False)
    
    # Formatear la tabla para que se vea limpia
    st.dataframe(
        q_df,
        column_config={
            "Query": "Consultas principales",
            "Clicks": st.column_config.NumberColumn("Clics", format="%d ⬇"),
            "Impresiones": "Impresiones"
        },
        hide_index=True,
        use_container_width=True
    )
st.markdown('</div>', unsafe_allow_html=True)

# --- PANEL EDUCATIVO ---
st.divider()
with st.expander("📚 Guía para el alumno: Cómo leer este gráfico"):
    st.write("""
    1. **La línea azul (Clics)**: Indica cuántas personas entraron a tu web.
    2. **La línea morada (Impresiones)**: Indica cuántas veces apareciste en los resultados de búsqueda.
    3. **Análisis**: Si las impresiones suben pero los clics no, significa que apareces pero tu título no es atractivo (necesitas mejorar el SEO On-page).
    """)
