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
    dates = pd.date_range(end=datetime.now(), periods=180)
    
    queries_config = {
        "Sitio 1: Ecommerce (Caída Técnica)": {"comprar laptop": 0.6, "pc gaming": 0.25, "teclado mecanico": 0.1, "monitor 4k": 0.05},
        "Sitio 2: Blog (Problema de CTR)": {"que es ddos": 0.5, "phishing ejemplos": 0.3, "encriptacion datos": 0.15, "seguridad informatica": 0.05},
        "Sitio 3: Nicho Dev (Oportunidad)": {"configurar neovim 2026": 0.7, "rust vs go": 0.2, "docker raspberry pi": 0.1}
    }
    
    perf_list = []
    current_qs = queries_config.get(scenario_name, {"query dummy": 1.0})
    
    for date in dates:
        # LÓGICA DE CAÍDA REALISTA (Día 120+)
        is_drop = (scenario_name == "Sitio 1: Ecommerce (Caída Técnica)" and date > dates[120])
        
        # Multiplicador de visibilidad técnica (Si no hay páginas indexadas, no hay nada)
        # En el escenario 1, después del día 120, la visibilidad cae al 5% residual
        tech_visibility = 0.05 if is_drop else 1.0
        
        for q, weight in current_qs.items():
            base_imp = 2000 * weight if scenario_name != "Sitio 3: Nicho Dev (Oportunidad)" else 100 * weight
            
            # Las impresiones ahora dependen de la salud técnica
            imp = int((base_imp + np.random.normal(0, base_imp * 0.1)) * tech_visibility)
            
            if is_drop:
                pos = np.random.uniform(40, 80) # Posiciones caen al fondo
                ctr = np.random.uniform(0.001, 0.005)
            elif scenario_name == "Sitio 2: Blog (Problema de CTR)":
                pos = np.random.uniform(1.1, 2.5)
                ctr = np.random.uniform(0.005, 0.012)
            else:
                pos = np.random.uniform(2.0, 6.0)
                ctr = np.random.uniform(0.08, 0.15)
            
            clicks = int(imp * ctr)
            perf_list.append([date, q, clicks, imp, pos, "México", "Mobile"])
            
    df_perf = pd.DataFrame(perf_list, columns=['Fecha', 'Query', 'Clicks', 'Impresiones', 'Posicion', 'Pais', 'Dispositivo'])
    
    # 2. Lógica de Indexación coincidente
    idx_list = []
    for date in dates:
        if scenario_name == "Sitio 1: Ecommerce (Caída Técnica)" and date > dates[120]:
            v = max(0, 800 - ((date - dates[120]).days * 25)) # Desindexación rápida
            e = 10 + ((date - dates[120]).days * 20) # Errores suben
        elif scenario_name == "Sitio 2: Blog (Problema de CTR)":
            v, e = 2500, 12
        else:
            v, e = 120, 0
        idx_list.append([date, int(v), int(e)])
        
    return df_perf, pd.DataFrame(idx_list, columns=['Fecha', 'Validas', 'Errores'])

# --- INTERFAZ ---
st.sidebar.title("🧪 GSC Lab v3.0")
sc_name = st.sidebar.selectbox("Elegir Escenario:", ["Sitio 1: Ecommerce (Caída Técnica)", "Sitio 2: Blog (Problema de CTR)", "Sitio 3: Nicho Dev (Oportunidad)"])
time_range = st.sidebar.selectbox("Periodo:", ["Últimos 28 días", "Últimos 3 meses", "Últimos 6 meses"])

# Filtrado
days_map = {"Últimos 28 días": 28, "Últimos 3 meses": 90, "Últimos 6 meses": 180}
cutoff = datetime.now() - timedelta(days=days_map[time_range])
df_p_raw, df_i_raw = get_data(sc_name)
df_p = df_p_raw[df_p_raw['Fecha'] >= cutoff]
df_i = df_i_raw[df_i_raw['Fecha'] >= cutoff]

tab_p, tab_i, tab_t = st.tabs(["📊 Rendimiento", "🔍 Indexación", "👨‍🏫 Taller"])

with tab_p:
    st.subheader("Rendimiento")
    # El gráfico ahora mostrará la caída de AMBAS métricas en el Escenario 1
    st.plotly_chart(px.line(df_p.groupby('Fecha').sum().reset_index(), x='Fecha', y=['Clicks', 'Impresiones'], 
                           color_discrete_map={'Clicks': '#4285F4', 'Impresiones': '#7E3FF2'},
                           template="none"), use_container_width=True)
    st.dataframe(df_p.groupby('Query').agg({'Clicks':'sum','Impresiones':'sum','Posicion':'mean'}).sort_values('Clicks', ascending=False), use_container_width=True)

with tab_i:
    st.subheader("Cobertura")
    
    st.plotly_chart(px.area(df_idx := df_i, x='Fecha', y=['Validas', 'Errores'], 
                           color_discrete_map={'Validas':'#34A853', 'Errores':'#D93025'}, 
                           line_shape='hv', template="none"), use_container_width=True)

with tab_t:
    st.info(f"**Análisis para Docentes:** En el escenario '{sc_name}', observa cómo la línea de impresiones y clics se mueven en paralelo. Si ambas caen, el problema suele estar en la pestaña de Cobertura.")
