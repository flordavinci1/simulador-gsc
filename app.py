import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Search Console Simulator", layout="wide", page_icon="📈")

# --- CSS PARA REPLICAR LA ESTÉTICA GSC (FONDO GRIS, CAJAS BLANCAS) ---
st.markdown("""
    <style>
    .main { background-color: #f1f3f4; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #dadce0; }
    
    /* Tarjetas de Métricas */
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px 8px 0 0;
        border-bottom: 4px solid #4285f4;
        text-align: left;
        box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3);
    }
    .metric-label { font-size: 13px; color: #5f6368; font-weight: 500; }
    .metric-value { font-size: 24px; font-weight: 500; color: #202124; margin-top: 5px; }
    
    /* Contenedores */
    .gsc-container {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #dadce0;
        margin-bottom: 20px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background-color: white; border-bottom: 1px solid #dadce0; }
    .stTabs [data-baseweb="tab"] { font-weight: 500; color: #5f6368; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
@st.cache_data
def generate_data(scenario):
    dates = pd.date_range(end=datetime.now(), periods=180)
    
    # Queries Verosímiles
    queries_map = {
        "Ecommerce (Caída Técnica)": ["laptop gamer rtx", "teclado mecanico", "monitor 4k", "raton inalambrico"],
        "Blog (Bajo CTR)": ["que es phishing", "ataque ddos", "encriptacion de datos", "seguridad informatica"],
        "Nicho Dev (Oportunidad)": ["configurar neovim 2026", "rust vs go", "docker raspberry pi 5"]
    }
    
    q_list = queries_map.get(scenario, ["query dummy"])
    perf_records = []
    idx_records = []
    
    for date in dates:
        # Escenario de Caída
        is_drop = (scenario == "Ecommerce (Caída Técnica)" and date > dates[120])
        
        for q in q_list:
            imp = np.random.randint(1000, 1500) if scenario != "Nicho Dev (Oportunidad)" else np.random.randint(50, 100)
            if is_drop:
                clicks, pos = np.random.randint(0, 2), np.random.uniform(25, 45)
            elif scenario == "Blog (Bajo CTR)":
                clicks, pos = np.random.randint(1, 10), np.random.uniform(1.5, 3.2)
            else:
                clicks, pos = int(imp * np.random.uniform(0.15, 0.25)), np.random.uniform(1.1, 2.5)
            perf_records.append([date, q, clicks, imp, pos])
        
        # Datos de Indexación
        if is_drop:
            v, e = max(0, 500 - (date - dates[120]).days * 15), 5 + (date - dates[120]).days * 12
        else:
            v, e = (1200 if scenario == "Blog (Bajo CTR)" else 500), np.random.randint(0, 5)
        idx_records.append([date, v, e])
            
    return pd.DataFrame(perf_records, columns=['Fecha','Query','Clicks','Impresiones','Posicion']), \
           pd.DataFrame(idx_records, columns=['Fecha','Validas','Errores'])

# --- SIDEBAR (NAVEGACIÓN) ---
with st.sidebar:
    st.image("https://www.gstatic.com/images/branding/googlelogo/svg/googlelogo_clr_74x24dp.svg", width=100)
    st.subheader("Search Console")
    menu = st.radio("Menú", ["📈 Rendimiento", "🔍 Indexación", "👨‍🏫 Guía Estratégica", "📤 Cargar Datos"])
    st.divider()
    scenario = st.selectbox("Escenario de aprendizaje:", ["Ecommerce (Caída Técnica)", "Blog (Bajo CTR)", "Nicho Dev (Oportunidad)"])
    
df_perf, df_idx = generate_data(scenario)

# --- PANTALLA: RENDIMIENTO ---
if menu == "📈 Rendimiento":
    st.title("Rendimiento")
    st.caption("Tipo de búsqueda: Web | Fecha: Últimos 6 meses")
    
    # Tarjetas GSC Style
    total_c = df_perf['Clicks'].sum()
    total_i = df_perf['Impresiones'].sum()
    avg_ctr = (total_c / total_i) * 100
    avg_p = df_perf['Posicion'].mean()
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="metric-card" style="border-bottom-color: #4285f4;"><div class="metric-label">☑ Clics totales</div><div class="metric-value">{total_c:,}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="metric-card" style="border-bottom-color: #7e3ff2;"><div class="metric-label">☑ Impresiones totales</div><div class="metric-value">{total_i/1000:.1f} mil</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="metric-card" style="border-bottom-color: #00897b;"><div class="metric-label">☐ CTR medio</div><div class="metric-value">{avg_ctr:.1f}%</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="metric-card" style="border-bottom-color: #e8710a;"><div class="metric-label">☐ Posición media</div><div class="metric-value">{avg_p:.1f}</div></div>', unsafe_allow_html=True)

    # Gráfico
    st.markdown('<div class="gsc-container">', unsafe_allow_html=True)
    trend = df_perf.groupby('Fecha').agg({'Clicks':'sum', 'Impresiones':'sum'}).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=trend['Fecha'], y=trend['Clicks'], name="Clics", line=dict(color='#4285f4', width=2)))
    fig.add_trace(go.Scatter(x=trend['Fecha'], y=trend['Impresiones'], name="Impresiones", line=dict(color='#7e3ff2', width=2), yaxis="y2"))
    fig.update_layout(yaxis=dict(title="Clics"), yaxis2=dict(overlaying="y", side="right"), 
                      hovermode="x unified", plot_bgcolor='white', height=400, margin=dict(l=0,r=0,t=20,b=0))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Tabla de Consultas
    st.markdown('<div class="gsc-container">', unsafe_allow_html=True)
    tabs = st.tabs(["CONSULTAS", "PÁGINAS", "PAÍSES", "DISPOSITIVOS"])
    with tabs[0]:
        q_df = df_perf.groupby('Query').agg({'Clicks':'sum', 'Impresiones':'sum', 'Posicion':'mean'}).sort_values('Clicks', ascending=False)
        st.dataframe(q_df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- PANTALLA: INDEXACIÓN ---
elif menu == "🔍 Indexación":
    st.title("Indexación de páginas")
    
    col_idx1, col_idx2 = st.columns(2)
    with col_idx1: st.markdown(f'<div class="metric-card" style="border-bottom-color: #34a853;"><div class="metric-label">Páginas indexadas</div><div class="metric-value">{df_idx.iloc[-1]["Validas"]}</div></div>', unsafe_allow_html=True)
    with col_idx2: st.markdown(f'<div class="metric-card" style="border-bottom-color: #ea4335;"><div class="metric-label">Páginas no indexadas</div><div class="metric-value">{df_idx.iloc[-1]["Errores"]}</div></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="gsc-container">', unsafe_allow_html=True)
    
    fig_idx = px.area(df_idx, x='Fecha', y=['Validas', 'Errores'], color_discrete_map={'Validas':'#34a853', 'Errores':'#ea4335'}, line_shape='hv')
    fig_idx.update_layout(plot_bgcolor='white')
    st.plotly_chart(fig_idx, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- PANTALLA: ESTRATEGIA ---
elif menu == "👨‍🏫 Guía Estratégica":
    st.title("Libro del Profesor")
    if scenario == "Ecommerce (Caída Técnica)":
        st.error("Escenario: Crisis de Indexación")
        st.write("**Diagnóstico:** El sitio perdió el 80% de sus páginas válidas en 30 días. Los clics cayeron a cero.")
        st.write("**Acción:** Revisar el servidor y el archivo robots.txt.")
    elif scenario == "Blog (Bajo CTR)":
        st.warning("Escenario: Crisis de CTR")
        st.write("**Diagnóstico:** Muchas impresiones pero nadie hace clic. El ranking es bueno pero el título es malo.")
        st.write("**Acción:** Reescribir Meta Titles.")
    else:
        st.success("Escenario: Oportunidad de Nicho")
        st.write("**Diagnóstico:** CTR altísimo. Google ama este contenido. Falta volumen.")
        st.write("**Acción:** Buscar palabras clave relacionadas con más volumen.")

# --- PANTALLA: CARGAR DATOS ---
else:
    st.title("Laboratorio de Datos")
    st.write("Sube tu propio archivo CSV para analizarlo con la interfaz de GSC.")
    uploaded = st.file_uploader("Archivo CSV (Columnas: Fecha, Query, Clicks, Impresiones, Posicion)")
    if uploaded:
        st.success("¡Datos cargados correctamente! Ve a la pestaña de Rendimiento.")
