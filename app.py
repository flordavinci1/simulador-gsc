import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="GSC Lab - Pro Edition", layout="wide", page_icon="🧪")

# --- GENERADOR DE ESCENARIOS VEROSÍMILES ---
@st.cache_data
def get_data(scenario_name):
    dates = pd.date_range(end=datetime.now(), periods=180)
    
    # Queries con "Pesos" para verosimilitud (Query: Peso de importancia)
    queries_config = {
        "Sitio 1: Ecommerce (Caída Técnica)": {"comprar laptop": 0.6, "pc gaming": 0.25, "teclado mecanico": 0.1, "monitor 4k": 0.05},
        "Sitio 2: Blog (Problema de CTR)": {"que es ddos": 0.5, "phishing ejemplos": 0.3, "encriptacion datos": 0.15, "seguridad informatica": 0.05},
        "Sitio 3: Nicho Dev (Oportunidad)": {"configurar neovim 2026": 0.7, "rust vs go": 0.2, "docker raspberry pi": 0.1}
    }
    
    perf_list = []
    current_qs = queries_config.get(scenario_name, {"query dummy": 1.0})
    
    for date in dates:
        # Lógica de caída (Día 120+)
        is_drop = (scenario_name == "Sitio 1: Ecommerce (Caída Técnica)" and date > dates[120])
        
        for q, weight in current_qs.items():
            # Impresiones base según el peso de la query
            base_imp = 2000 * weight if scenario_name != "Sitio 3: Nicho Dev (Oportunidad)" else 100 * weight
            imp = int(base_imp + np.random.normal(0, base_imp * 0.1)) # Variación natural
            
            if is_drop:
                # En caída técnica, la posición se desploma y los clics mueren
                pos = np.random.uniform(30, 60)
                ctr = np.random.uniform(0.0001, 0.001)
            elif scenario_name == "Sitio 2: Blog (Problema de CTR)":
                # Posición alta pero CTR muy bajo (típico de meta titles malos)
                pos = np.random.uniform(1.1, 2.5)
                ctr = np.random.uniform(0.005, 0.012)
            elif scenario_name == "Sitio 3: Nicho Dev (Oportunidad)":
                # Poco volumen pero CTR estelar (Nicho perfecto)
                pos = np.random.uniform(1.0, 1.8)
                ctr = np.random.uniform(0.20, 0.35)
            else:
                # Comportamiento estándar saludable
                pos = np.random.uniform(2.0, 6.0)
                ctr = np.random.uniform(0.08, 0.15)
            
            clicks = int(imp * ctr)
            
            # Reparto verosímil por País y Dispositivo
            paises = ["México", "España", "Colombia", "Argentina", "Chile"]
            pesos_paises = [0.35, 0.25, 0.2, 0.1, 0.1]
            
            dispositivos = ["Mobile", "Desktop", "Tablet"]
            pesos_disp = [0.65, 0.30, 0.05]
            
            for _ in range(max(1, int(clicks/5))): # Fragmentamos los datos para las tablas
                p = np.random.choice(paises, p=pesos_paises)
                d = np.random.choice(dispositivos, p=pesos_disp)
                perf_list.append([date, q, max(1, int(clicks/len(paises))), int(imp/len(paises)), pos, p, d])
            
    df_perf = pd.DataFrame(perf_list, columns=['Fecha', 'Query', 'Clicks', 'Impresiones', 'Posicion', 'Pais', 'Dispositivo'])
    
    # 2. Lógica de Indexación (Relación técnica)
    idx_list = []
    for date in dates:
        if scenario_name == "Sitio 1: Ecommerce (Caída Técnica)" and date > dates[120]:
            # Las páginas válidas caen mientras los errores suben (Migración fallida)
            v = max(0, 800 - ((date - dates[120]).days * 20))
            e = 10 + ((date - dates[120]).days * 15)
        elif scenario_name == "Sitio 2: Blog (Problema de CTR)":
            v, e = 2500, 12 # Sitio grande y estable
        else:
            v, e = 120, 0 # Sitio pequeño y limpio
        idx_list.append([date, int(v), int(e)])
        
    df_idx = pd.DataFrame(idx_list, columns=['Fecha', 'Validas', 'Errores'])
    return df_perf, df_idx

# --- SIDEBAR ---
st.sidebar.title("🧪 GSC Lab v2.0")
sc_name = st.sidebar.selectbox("Elegir Escenario Educativo:", [
    "Sitio 1: Ecommerce (Caída Técnica)", 
    "Sitio 2: Blog (Problema de CTR)", 
    "Sitio 3: Nicho Dev (Oportunidad)"
])

df_perf, df_idx = get_data(sc_name)

# --- TABS PRINCIPALES ---
tab_perf, tab_idx, tab_teacher = st.tabs(["📊 Rendimiento", "🔍 Indexación", "👨‍🏫 Libro del Profesor"])

with tab_perf:
    st.subheader("Rendimiento de búsqueda")
    
    # KPIs con formato profesional
    c1, c2, c3, c4 = st.columns(4)
    total_clicks = df_perf['Clicks'].sum()
    total_impressions = df_perf['Impresiones'].sum()
    
    c1.metric("Clicks totales", f"{total_clicks:,}")
    c2.metric("Impresiones totales", f"{total_impressions:,}")
    c3.metric("CTR medio", f"{(total_clicks/total_impressions)*100:.2f}%")
    c4.metric("Posición media", f"{df_perf['Posicion'].mean():.1f}")
    
    # Gráfico de líneas (Rendimiento temporal)
    st.plotly_chart(px.line(df_perf.groupby('Fecha').sum().reset_index(), x='Fecha', y=['Clicks', 'Impresiones'], 
                           color_discrete_map={'Clicks': '#4285F4', 'Impresiones': '#7E3FF2'},
                           template="none"), use_container_width=True)

    # --- TABLAS DE DIMENSIONES ---
    st.divider()
    sub_tabs = st.tabs(["Consultas", "Páginas", "Países", "Dispositivos"])

    with sub_tabs[0]: # Consultas
        q_analysis = df_perf.groupby('Query').agg({'Clicks':'sum', 'Impresiones':'sum', 'Posicion':'mean'}).sort_values(by='Clicks', ascending=False)
        q_analysis['CTR'] = (q_analysis['Clicks'] / q_analysis['Impresiones']) * 100
        st.dataframe(q_analysis[['Clicks', 'Impresiones', 'CTR', 'Posicion']].style.format(precision=2), use_container_width=True)

    with sub_tabs[1]: # Páginas
        df_perf['Página'] = "/" + df_perf['Query'].str.replace(" ", "-")
        p_analysis = df_perf.groupby('Página').agg({'Clicks':'sum', 'Impresiones':'sum', 'Posicion':'mean'}).sort_values(by='Clicks', ascending=False)
        st.dataframe(p_analysis.style.format(precision=2), use_container_width=True)

    with sub_tabs[2]: # Países
        pa_analysis = df_perf.groupby('Pais').agg({'Clicks':'sum', 'Impresiones':'sum'}).sort_values(by='Clicks', ascending=False)
        st.dataframe(pa_analysis, use_container_width=True)

    with sub_tabs[3]: # Dispositivos
        d_analysis = df_perf.groupby('Dispositivo').agg({'Clicks':'sum', 'Impresiones':'sum'}).sort_values(by='Clicks', ascending=False)
        st.dataframe(d_analysis, use_container_width=True)

with tab_idx:
    st.subheader("Estado de Cobertura (Indexación)")
    
    st.plotly_chart(px.area(df_idx, x='Fecha', y=['Validas', 'Errores'], 
                           color_discrete_map={'Validas':'#34A853', 'Errores':'#D93025'}, 
                           line_shape='hv', template="none"), use_container_width=True)

with tab_teacher:
    st.header("Guía para el Instructor")
    guides = {
        "Sitio 1: Ecommerce (Caída Técnica)": {
            "Hallazgo": "Caída del 90% en tráfico. Si miras Indexación, las 'Válidas' caen y los 'Errores' suben.",
            "Diagnóstico": "Migración fallida o cambio masivo de URLs sin redirección.",
            "Acción": "Implementar 301s y revisar errores 404 en el servidor."
        },
        "Sitio 2: Blog (Problema de CTR)": {
            "Hallazgo": "Impresiones muy altas pero pocos clics. CTR < 1%.",
            "Diagnóstico": "Títulos poco atractivos o que no coinciden con la intención de búsqueda.",
            "Acción": "Optimizar Snippets (SEO On-Page)."
        },
        "Sitio 3: Nicho Dev (Oportunidad)": {
            "Hallazgo": "Posición 1 constante. CTR del 25%. Volumen bajísimo.",
            "Diagnóstico": "Dominio total de una keyword de nicho.",
            "Acción": "Buscar keywords relacionadas con más volumen para escalar."
        }
    }
    g = guides[sc_name]
    st.info(f"**Observación:** {g['Hallazgo']}")
    st.warning(f"**Causa Raíz:** {g['Diagnóstico']}")
    st.success(f"**Tarea para los alumnos:** {g['Acción']}")

st.sidebar.divider()
st.sidebar.download_button("📥 Exportar Datos (CSV)", df_perf.to_csv(index=False), "gsc_data.csv")
