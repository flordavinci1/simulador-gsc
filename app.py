import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="GSC Lab - Pro Edition", layout="wide", page_icon="🧪")

# --- GENERADOR DE ESCENARIOS ---
@st.cache_data
def get_data(scenario_name):
    dates = pd.date_range(end=datetime.now(), periods=180)
    
    # 1. Lógica de Rendimiento
    queries = {
        "Sitio 1: Ecommerce (Caída Técnica)": ["comprar laptop", "pc gaming", "teclado mecanico", "monitor 4k"],
        "Sitio 2: Blog (Problema de CTR)": ["que es ddos", "phishing ejemplos", "encriptacion datos", "seguridad informatica"],
        "Sitio 3: Nicho Dev (Oportunidad)": ["configurar neovim 2026", "rust vs go", "docker raspberry pi"]
    }
    
    perf_list = []
    current_qs = queries.get(scenario_name, ["query dummy"])
    
    for date in dates:
        is_drop = (scenario_name == "Sitio 1: Ecommerce (Caída Técnica)" and date > dates[120])
        for q in current_qs:
            imp = np.random.randint(1000, 1500) if scenario_name != "Sitio 3" else np.random.randint(40, 80)
            if is_drop:
                clicks, pos = np.random.randint(0, 3), np.random.uniform(25, 55)
            elif scenario_name == "Sitio 2: Blog (Problema de CTR)":
                clicks, pos = np.random.randint(1, 8), np.random.uniform(1.5, 3.5)
            else:
                clicks = int(imp * np.random.uniform(0.1, 0.15))
                pos = np.random.uniform(1.1, 4.0)
            
            # Añadimos dimensiones extra de forma aleatoria pero coherente
            pais = np.random.choice(["España", "México", "Argentina", "Colombia", "Chile"])
            dispositivo = np.random.choice(["Mobile", "Desktop", "Tablet"], p=[0.6, 0.3, 0.1])
            
            perf_list.append([date, q, clicks, imp, pos, pais, dispositivo])
            
    df_perf = pd.DataFrame(perf_list, columns=['Fecha', 'Query', 'Clicks', 'Impresiones', 'Posicion', 'Pais', 'Dispositivo'])
    
    # 2. Lógica de Indexación
    idx_list = []
    for date in dates:
        if scenario_name == "Sitio 1: Ecommerce (Caída Técnica)" and date > dates[120]:
            v, e = 500 - ((date - dates[120]).days * 12), 10 + ((date - dates[120]).days * 10)
        elif scenario_name == "Sitio 2: Blog (Problema de CTR)":
            v, e = 1500, 2
        else:
            v, e = 60, 0
        idx_list.append([date, max(0, int(v)), int(e)])
        
    df_idx = pd.DataFrame(idx_list, columns=['Fecha', 'Validas', 'Errores'])
    return df_perf, df_idx

# --- SIDEBAR ---
st.sidebar.title("🧪 GSC Educational Lab")
mode = st.sidebar.radio("Origen de datos:", ["Escenarios Predefinidos", "Subir mi Dummy Data (CSV)"])

if mode == "Escenarios Predefinidos":
    sc_name = st.sidebar.selectbox("Elegir Escenario:", [
        "Sitio 1: Ecommerce (Caída Técnica)", 
        "Sitio 2: Blog (Problema de CTR)", 
        "Sitio 3: Nicho Dev (Oportunidad)"
    ])
    df_perf, df_idx = get_data(sc_name)
else:
    up = st.sidebar.file_uploader("Sube tu CSV (Debe tener: Fecha, Query, Clicks, Impresiones, Posicion)")
    if up:
        df_perf = pd.read_csv(up, parse_dates=['Fecha'])
        # Asegurar que existan columnas Pais y Dispositivo si no vienen en el CSV
        if 'Pais' not in df_perf.columns: df_perf['Pais'] = "Desconocido"
        if 'Dispositivo' not in df_perf.columns: df_perf['Dispositivo'] = "Desktop"
        df_idx = pd.DataFrame({'Fecha': df_perf['Fecha'].unique(), 'Validas': 100, 'Errores': 0})
        sc_name = "Datos Externos"
    else:
        st.info("Esperando archivo... usando Escenario 1 por defecto.")
        sc_name = "Sitio 1: Ecommerce (Caída Técnica)"
        df_perf, df_idx = get_data(sc_name)

# --- TABS PRINCIPALES ---
tab_perf, tab_idx, tab_teacher = st.tabs(["📊 Rendimiento", "🔍 Indexación", "👨‍🏫 Libro del Profesor"])

with tab_perf:
    st.subheader("Análisis de Tráfico")
    c1, c2, c3, c4 = st.columns(4)
    total_clicks = df_perf['Clicks'].sum()
    total_impressions = df_perf['Impresiones'].sum()
    
    c1.metric("Clicks", f"{total_clicks:,}")
    c2.metric("Impresiones", f"{total_impressions:,}")
    c3.metric("CTR", f"{(total_clicks/total_impressions)*100:.2f}%")
    c4.metric("Posición Media", f"{df_perf['Posicion'].mean():.1f}")
    
    st.plotly_chart(px.line(df_perf.groupby('Fecha').sum().reset_index(), x='Fecha', y=['Clicks', 'Impresiones'], color_discrete_sequence=['#4285F4', '#EA4335']), use_container_width=True)

    # --- SECCIÓN NUEVA: TABLAS DE DIMENSIONES ---
    st.divider()
    sub_tab_queries, sub_tab_paginas, sub_tab_paises, sub_tab_dispositivos = st.tabs(["Consultas", "Páginas", "Países", "Dispositivos"])

    with sub_tab_queries:
        q_analysis = df_perf.groupby('Query').agg({'Clicks':'sum', 'Impresiones':'sum', 'Posicion':'mean'}).sort_values(by='Clicks', ascending=False)
        q_analysis['CTR'] = (q_analysis['Clicks'] / q_analysis['Impresiones']) * 100
        st.dataframe(q_analysis[['Clicks', 'Impresiones', 'CTR', 'Posicion']].style.format(precision=2), use_container_width=True)

    with sub_tab_paginas:
        # Simulamos páginas a partir de las queries para fines educativos
        df_perf['Página'] = "/" + df_perf['Query'].str.replace(" ", "-")
        p_analysis = df_perf.groupby('Página').agg({'Clicks':'sum', 'Impresiones':'sum', 'Posicion':'mean'}).sort_values(by='Clicks', ascending=False)
        st.dataframe(p_analysis.style.format(precision=2), use_container_width=True)

    with sub_tab_paises:
        pa_analysis = df_perf.groupby('Pais').agg({'Clicks':'sum', 'Impresiones':'sum'}).sort_values(by='Clicks', ascending=False)
        st.dataframe(pa_analysis, use_container_width=True)

    with sub_tab_dispositivos:
        d_analysis = df_perf.groupby('Dispositivo').agg({'Clicks':'sum', 'Impresiones':'sum'}).sort_values(by='Clicks', ascending=False)
        st.dataframe(d_analysis, use_container_width=True)

with tab_idx:
    st.subheader("Estado de Cobertura")
    st.plotly_chart(px.area(df_idx, x='Fecha', y=['Validas', 'Errores'], color_discrete_map={'Validas':'#34A853', 'Errores':'#D93025'}, line_shape='hv'), use_container_width=True)

with tab_teacher:
    st.header("Guía de Resolución para el Escenario")
    guides = {
        "Sitio 1: Ecommerce (Caída Técnica)": {
            "Hallazgo": "Caída drástica de clicks correlacionada con aumento de errores de indexación.",
            "Causa Probable": "Migración mal ejecutada o desindexación por error en robots.txt.",
            "Acciones": ["Revisar logs del servidor", "Validar redirecciones 301", "Inspeccionar URLs en GSC"]
        },
        "Sitio 2: Blog (Problema de CTR)": {
            "Hallazgo": "Impresiones masivas y posiciones top 3, pero CTR bajísimo (< 1%).",
            "Causa Probable": "Snippets poco atractivos o que no responden a la intención de búsqueda.",
            "Acciones": ["Optimizar Meta Titles con copywriting", "Añadir Datos Estructurados (FAQ)", "Analizar competidores"]
        },
        "Sitio 3: Nicho Dev (Oportunidad)": {
            "Hallazgo": "Poco volumen pero CTR muy alto y posición media excelente.",
            "Causa Probable": "Alta relevancia para una audiencia muy específica.",
            "Acciones": ["Escalar contenido a temas relacionados", "Buscar keywords 'Seed' con más volumen"]
        }
    }
    
    current_guide = guides.get(sc_name, {"Hallazgo": "Datos externos", "Causa Probable": "N/A", "Acciones": []})
    st.info(f"**Análisis:** {current_guide['Hallazgo']}")
    st.warning(f"**Hipótesis:** {current_guide['Causa Probable']}")
    st.write("**Plan de Acción Sugerido:**")
    for step in current_guide['Acciones']:
        st.write(f"- {step}")

st.sidebar.download_button("📥 Descargar CSV de este escenario", df_perf.to_csv(index=False), "dummy_gsc.csv")
