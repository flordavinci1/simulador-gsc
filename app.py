import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="GSC Lab - Pro Edition", layout="wide", page_icon="🧪")

# --- GENERADOR DE ESCENARIOS CORREGIDO ---
@st.cache_data
def get_data(scenario_name):
    # Generamos 6 meses de datos base
    dates = pd.date_range(end=datetime.now(), periods=180)
    
    queries_config = {
        "Sitio 1: Ecommerce (Caída Técnica)": {"comprar laptop": 0.6, "pc gaming": 0.25, "teclado mecanico": 0.1, "monitor 4k": 0.05},
        "Sitio 2: Blog (Problema de CTR)": {"que es ddos": 0.5, "phishing ejemplos": 0.3, "encriptacion datos": 0.15, "seguridad informatica": 0.05},
        "Sitio 3: Nicho Dev (Oportunidad)": {"configurar neovim 2026": 0.7, "rust vs go": 0.2, "docker raspberry pi": 0.1}
    }
    
    perf_list = []
    current_qs = queries_config.get(scenario_name, {"query dummy": 1.0})
    
    for date in dates:
        # LÓGICA DE CAÍDA (Día 120+)
        is_drop = (scenario_name == "Sitio 1: Ecommerce (Caída Técnica)" and date > dates[120])
        tech_visibility = 0.05 if is_drop else 1.0
        
        for q, weight in current_qs.items():
            base_imp = 2000 * weight if scenario_name != "Sitio 3: Nicho Dev (Oportunidad)" else 120 * weight
            # Las impresiones caen si hay problemas técnicos
            imp = int((base_imp + np.random.normal(0, base_imp * 0.1)) * tech_visibility)
            
            if is_drop:
                pos = np.random.uniform(40, 80)
                ctr = np.random.uniform(0.001, 0.005)
            elif scenario_name == "Sitio 2: Blog (Problema de CTR)":
                pos = np.random.uniform(1.1, 2.5)
                ctr = np.random.uniform(0.005, 0.009)
            else:
                pos = np.random.uniform(1.0, 2.0)
                ctr = np.random.uniform(0.18, 0.28)
            
            clicks = int(imp * ctr)
            perf_list.append([date, q, clicks, imp, pos, "México", "Mobile"])
            
    df_perf = pd.DataFrame(perf_list, columns=['Fecha', 'Query', 'Clicks', 'Impresiones', 'Posicion', 'Pais', 'Dispositivo'])
    
    # Lógica de Indexación
    idx_list = []
    for date in dates:
        if scenario_name == "Sitio 1: Ecommerce (Caída Técnica)" and date > dates[120]:
            v = max(0, 800 - ((date - dates[120]).days * 25))
            e = 10 + ((date - dates[120]).days * 20)
        elif scenario_name == "Sitio 2: Blog (Problema de CTR)":
            v, e = 2500, 12
        else:
            v, e = 150, 0
        idx_list.append([date, int(v), int(e)])
        
    return df_perf, pd.DataFrame(idx_list, columns=['Fecha', 'Validas', 'Errores'])

# --- SIDEBAR (CONTROL DE TIEMPO Y ESCENARIO) ---
st.sidebar.title("🧪 GSC Lab v3.1")
sc_name = st.sidebar.selectbox("Elegir Escenario:", ["Sitio 1: Ecommerce (Caída Técnica)", "Sitio 2: Blog (Problema de CTR)", "Sitio 3: Nicho Dev (Oportunidad)"])

st.sidebar.divider()
st.sidebar.subheader("Filtro de Tiempo")
time_range = st.sidebar.selectbox("Periodo:", ["Últimos 28 días", "Últimos 3 meses", "Últimos 6 meses"])

# Lógica del filtro
days_map = {"Últimos 28 días": 28, "Últimos 3 meses": 90, "Últimos 6 meses": 180}
cutoff = datetime.now() - timedelta(days=days_map[time_range])

# Cargar y filtrar datos
df_p_raw, df_i_raw = get_data(sc_name)
df_p = df_p_raw[df_p_raw['Fecha'] >= cutoff]
df_i = df_i_raw[df_i_raw['Fecha'] >= cutoff]

# --- TABS PRINCIPALES ---
tab_perf, tab_idx, tab_teacher = st.tabs(["📊 Rendimiento", "🔍 Indexación", "👨‍🏫 Libro del Profesor"])

with tab_perf:
    st.subheader(f"Rendimiento de búsqueda ({time_range})")
    
    # TARJETAS DE DATA GENERAL (Restauradas)
    c1, c2, c3, c4 = st.columns(4)
    total_clicks = df_p['Clicks'].sum()
    total_impressions = df_p['Impresiones'].sum()
    avg_pos = df_p['Posicion'].mean()
    
    c1.metric("Clics totales", f"{total_clicks:,}")
    c2.metric("Impresiones totales", f"{total_impressions:,}")
    c3.metric("CTR medio", f"{(total_clicks/total_impressions)*100:.2f}%")
    c4.metric("Posición media", f"{avg_pos:.1f}")
    
    # Gráfico de rendimiento
    # Aquí verás que en el Escenario 1, AMBAS líneas caen juntas
    
    st.plotly_chart(px.line(df_p.groupby('Fecha').sum().reset_index(), x='Fecha', y=['Clicks', 'Impresiones'], 
                           color_discrete_map={'Clicks': '#4285F4', 'Impresiones': '#7E3FF2'},
                           template="none"), use_container_width=True)

    # Tablas de dimensiones
    st.divider()
    sub_tabs = st.tabs(["Consultas", "Páginas", "Países", "Dispositivos"])
    with sub_tabs[0]:
        q_analysis = df_p.groupby('Query').agg({'Clicks':'sum', 'Impresiones':'sum', 'Posicion':'mean'}).sort_values(by='Clicks', ascending=False)
        q_analysis['CTR'] = (q_analysis['Clicks'] / q_analysis['Impresiones']) * 100
        st.dataframe(q_analysis[['Clicks', 'Impresiones', 'CTR', 'Posicion']].style.format(precision=2), use_container_width=True)
    with sub_tabs[1]:
        df_p['Página'] = "/" + df_p['Query'].str.replace(" ", "-")
        st.dataframe(df_p.groupby('Página').agg({'Clicks':'sum', 'Impresiones':'sum', 'Posicion':'mean'}).sort_values(by='Clicks', ascending=False).style.format(precision=2), use_container_width=True)

with tab_idx:
    st.subheader("Estado de Cobertura")
    # Tarjetas de indexación para diagnóstico rápido
    ci1, ci2 = st.columns(2)
    ci1.metric("Páginas Válidas", f"{df_i.iloc[-1]['Validas']:,}")
    ci2.metric("Páginas con Error", f"{df_i.iloc[-1]['Errores']:,}", delta_color="inverse")

    
    st.plotly_chart(px.area(df_i, x='Fecha', y=['Validas', 'Errores'], 
                           color_discrete_map={'Validas':'#34A853', 'Errores':'#D93025'}, 
                           line_shape='hv', template="none"), use_container_width=True)

with tab_teacher:
    st.header("Guía para el Taller")
    guides = {
        "Sitio 1: Ecommerce (Caída Técnica)": {
            "Observación": "Ambas líneas (clics e impresiones) mueren. Es un apagón visual.",
            "Diagnóstico": "Problema de Indexación masivo. Mira la pestaña de Cobertura.",
            "Pregunta para alumnos": "¿Si el contenido fuera malo, caerían las impresiones tan rápido? No, solo caerían los clics."
        },
        "Sitio 2: Blog (Problema de CTR)": {
            "Observación": "Mucha impresión pero poquísimo clic. Posición excelente.",
            "Diagnóstico": "Títulos mediocres. El usuario ve el resultado pero no le interesa.",
            "Pregunta para alumnos": "¿Qué palabras usarías en el título para subir ese CTR?"
        },
        "Sitio 3: Nicho Dev (Oportunidad)": {
            "Observación": "Todo está en verde, pero los números son muy pequeños.",
            "Diagnóstico": "Contenido de alta calidad en un mercado de poco volumen.",
            "Pregunta para alumnos": "¿Cómo escalarías este éxito a keywords más genéricas?"
        }
    }
    g = guides[sc_name]
    st.info(f"**Análisis:** {g['Observación']}")
    st.warning(f"**Hipótesis:** {g['Diagnóstico']}")
    st.success(f"**Ejercicio:** {g['Pregunta para alumnos']}")

st.sidebar.divider()
st.sidebar.download_button("📥 Exportar Datos (CSV)", df_p.to_csv(index=False), "gsc_lab_data.csv")
