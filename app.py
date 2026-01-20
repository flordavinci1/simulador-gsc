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
    
    # Queries verosímiles por escenario
    queries = {
        "Sitio 1: Ecommerce (Caída Técnica)": ["comprar laptop gaming", "teclado mecanico rgb", "monitor 144hz", "grafica rtx 4080"],
        "Sitio 2: Blog (Problema de CTR)": ["que es un ataque ddos", "phishing ejemplos", "encriptacion de datos", "seguridad informatica"],
        "Sitio 3: Nicho Dev (Oportunidad)": ["configurar neovim 2026", "rust vs go backend", "docker raspberry pi 5"]
    }
    
    perf_list = []
    current_qs = queries.get(scenario_name, ["query dummy"])
    
    for date in dates:
        # Lógica de caída para el escenario 1
        is_drop = (scenario_name == "Sitio 1: Ecommerce (Caída Técnica)" and date > dates[120])
        
        for q in current_qs:
            # Volumen base
            imp = np.random.randint(1000, 1500) if scenario_name != "Sitio 3" else np.random.randint(50, 100)
            
            if is_drop:
                clicks, pos = np.random.randint(0, 2), np.random.uniform(25, 55)
            elif scenario_name == "Sitio 2: Blog (Problema de CTR)":
                clicks, pos = np.random.randint(1, 10), np.random.uniform(1.2, 3.0) # CTR bajo
            else:
                clicks = int(imp * np.random.uniform(0.12, 0.20)) # CTR alto
                pos = np.random.uniform(1.1, 3.5)
                
            perf_list.append([date, q, clicks, imp, pos])
            
    df_perf = pd.DataFrame(perf_list, columns=['Fecha', 'Query', 'Clicks', 'Impresiones', 'Posicion'])
    df_perf['CTR'] = (df_perf['Clicks'] / df_perf['Impresiones']) * 100
    
    # Lógica de Indexación
    idx_list = []
    for date in dates:
        if scenario_name == "Sitio 1: Ecommerce (Caída Técnica)" and date > dates[120]:
            v, e = 500 - ((date - dates[120]).days * 12), 10 + ((date - dates[120]).days * 10)
        elif scenario_name == "Sitio 2: Blog (Problema de CTR)":
            v, e = 1800, 4
        else:
            v, e = 85, 0
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
    up = st.sidebar.file_uploader("Sube tu CSV (Columnas: Fecha, Query, Clicks, Impresiones, Posicion)")
    if up:
        df_perf = pd.read_csv(up, parse_dates=['Fecha'])
        df_perf['CTR'] = (df_perf['Clicks'] / df_perf['Impresiones']) * 100
        df_idx = pd.DataFrame({'Fecha': df_perf['Fecha'].unique(), 'Validas': 100, 'Errores': 0})
        sc_name = "Datos Externos"
    else:
        st.info("Sube un CSV. Mientras tanto, usamos el Escenario 1.")
        sc_name = "Sitio 1: Ecommerce (Caída Técnica)"
        df_perf, df_idx = get_data(sc_name)

# --- TABS PRINCIPALES ---
tab_perf, tab_idx, tab_teacher = st.tabs(["📊 Rendimiento", "🔍 Indexación", "👨‍🏫 Libro del Profesor"])

with tab_perf:
    st.subheader("Rendimiento de búsqueda")
    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clicks", f"{df_perf['Clicks'].sum():,}")
    c2.metric("Impresiones", f"{df_perf['Impresiones'].sum():,}")
    c3.metric("CTR", f"{(df_perf['Clicks'].sum()/df_perf['Impresiones'].sum())*100:.2f}%")
    c4.metric("Posición Media", f"{df_perf['Posicion'].mean():.1f}")
    
    # Gráfico
    chart_df = df_perf.groupby('Fecha').agg({'Clicks':'sum', 'Impresiones':'sum'}).reset_index()
    st.plotly_chart(px.line(chart_df, x='Fecha', y=['Clicks', 'Impresiones'], 
                           color_discrete_map={'Clicks':'#4285F4', 'Impresiones':'#EA4335'},
                           template="plotly_white"), use_container_width=True)
    
    # TABLA DE PALABRAS CLAVE (QUERIES) - ¡VUELVE A ESTAR AQUÍ!
    st.divider()
    st.subheader("Detalle de Consultas (Queries)")
    q_table = df_perf.groupby('Query').agg({
        'Clicks': 'sum',
        'Impresiones': 'sum',
        'CTR': 'mean',
        'Posicion': 'mean'
    }).sort_values('Clicks', ascending=False)
    
    st.dataframe(q_table.style.format(precision=2), use_container_width=True)

with tab_idx:
    st.subheader("Estado de Cobertura de Indexación")
    st.plotly_chart(px.area(df_idx, x='Fecha', y=['Validas', 'Errores'], 
                           color_discrete_map={'Validas':'#34A853', 'Errores':'#D93025'}, 
                           line_shape='hv', template="plotly_white"), use_container_width=True)
    
    st.info("Páginas Válidas (Verde) vs Páginas con Error (Rojo).")

with tab_teacher:
    st.header("Guía para el Instructor")
    guides = {
        "Sitio 1: Ecommerce (Caída Técnica)": {
            "Hallazgo": "Caída de clicks y aumento de errores de indexación al mismo tiempo.",
            "Causa": "Problema técnico grave (posible error en servidor o archivo robots.txt).",
            "Acción": "Analizar la pestaña de Indexación y verificar códigos de estado HTTP (404/500)."
        },
        "Sitio 2: Blog (Problema de CTR)": {
            "Hallazgo": "Impresiones altas y buenas posiciones pero CTR bajísimo.",
            "Causa": "El contenido no es atractivo en los resultados de búsqueda.",
            "Acción": "Optimizar el 'Snippet' (Title y Meta Description) para hacerlo más clicable."
        },
        "Sitio 3: Nicho Dev (Oportunidad)": {
            "Hallazgo": "CTR muy alto en keywords muy específicas.",
            "Causa": "Audiencia fiel y contenido muy especializado.",
            "Acción": "Crear más contenido 'Long Tail' similar para dominar el nicho."
        }
    }
    
    if sc_name in guides:
        g = guides[sc_name]
        st.success(f"**Diagnóstico:** {g['Hallazgo']}")
        st.warning(f"**Hipótesis:** {g['Causa']}")
        st.write(f"**Sugerencia de clase:** {g['Action']}")
    else:
        st.write("Analizando datos externos cargados por el usuario.")

# --- SIDEBAR DOWNLOADS ---
st.sidebar.divider()
st.sidebar.subheader("Recursos")
# Generar CSV de ejemplo para que los profes lo descarguen como plantilla
template_csv = pd.DataFrame({
    'Fecha': ['2026-01-01', '2026-01-01'],
    'Query': ['ejemplo 1', 'ejemplo 2'],
    'Clicks': [10, 5],
    'Impresiones': [100, 200],
    'Posicion': [1.5, 8.2]
}).to_csv(index=False).encode('utf-8')

st.sidebar.download_button("📥 Descargar Plantilla CSV", template_csv, "plantilla_gsc.csv", "text/csv")
