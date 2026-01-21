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
        tech_visibility = 0.05 if is_drop else 1.0
        
        for q, weight in current_qs.items():
            base_imp = 4000 * weight if scenario_name != "Sitio 3: Nicho Dev (Oportunidad)" else 250 * weight
            imp = int((base_imp + np.random.normal(0, base_imp * 0.1)) * tech_visibility)
            
            if is_drop:
                pos = np.random.uniform(45, 85)
                ctr = np.random.uniform(0.0001, 0.0005)
            elif scenario_name == "Sitio 1: Ecommerce (Caída Técnica)":
                pos = np.random.uniform(3.5, 7.5)
                ctr = np.random.uniform(0.025, 0.045) # CTR REALISTA 2.5% - 4.5%
            elif scenario_name == "Sitio 2: Blog (Problema de CTR)":
                pos = np.random.uniform(1.2, 2.8)
                ctr = np.random.uniform(0.005, 0.009) # CTR BAJO < 1%
            else:
                pos = np.random.uniform(1.1, 2.1)
                ctr = np.random.uniform(0.09, 0.14) # CTR NICHO 9% - 14%
            
            clicks = int(imp * ctr)
            perf_list.append([date, q, clicks, imp, pos, "México", "Mobile"])
            
    df_perf = pd.DataFrame(perf_list, columns=['Fecha', 'Query', 'Clicks', 'Impresiones', 'Posicion', 'Pais', 'Dispositivo'])
    
    idx_list = []
    for date in dates:
        if scenario_name == "Sitio 1: Ecommerce (Caída Técnica)" and date > dates[120]:
            v = max(0, 800 - ((date - dates[120]).days * 25))
            e = 10 + ((date - dates[120]).days * 20)
        elif scenario_name == "Sitio 2: Blog (Problema de CTR)":
            v, e = 2800, 15
        else:
            v, e = 180, 0
        idx_list.append([date, int(v), int(e)])
        
    return df_perf, pd.DataFrame(idx_list, columns=['Fecha', 'Validas', 'Errores'])

# --- SIDEBAR ---
st.sidebar.title("🧪 GSC Lab v3.2")
sc_name = st.sidebar.selectbox("Elegir Escenario:", ["Sitio 1: Ecommerce (Caída Técnica)", "Sitio 2: Blog (Problema de CTR)", "Sitio 3: Nicho Dev (Oportunidad)"])
time_range = st.sidebar.selectbox("Periodo:", ["Últimos 28 días", "Últimos 3 meses", "Últimos 6 meses"])

# Filtrado de fechas
days_map = {"Últimos 28 días": 28, "Últimos 3 meses": 90, "Últimos 6 meses": 180}
cutoff = datetime.now() - timedelta(days=days_map[time_range])
df_p_raw, df_i_raw = get_data(sc_name)
df_p = df_p_raw[df_p_raw['Fecha'] >= cutoff]
df_i = df_i_raw[df_i_raw['Fecha'] >= cutoff]

# --- DASHBOARD ---
tab_perf, tab_idx, tab_teacher = st.tabs(["📊 Rendimiento", "🔍 Indexación", "👨‍🏫 Libro del Profesor"])

with tab_perf:
    st.subheader(f"Rendimiento de búsqueda ({time_range})")
    
    c1, c2, c3, c4 = st.columns(4)
    tc, ti = df_p['Clicks'].sum(), df_p['Impresiones'].sum()
    c1.metric("Clics totales", f"{tc:,}")
    c2.metric("Impresiones totales", f"{ti:,}")
    c3.metric("CTR medio", f"{(tc/ti)*100:.2f}%")
    c4.metric("Posición media", f"{df_p['Posicion'].mean():.1f}")
    
    # Gráfico de rendimiento sincronizado
    
    st.plotly_chart(px.line(df_p.groupby('Fecha').sum().reset_index(), x='Fecha', y=['Clicks', 'Impresiones'], 
                           color_discrete_map={'Clicks': '#4285F4', 'Impresiones': '#7E3FF2'},
                           template="none"), use_container_width=True)

    st.divider()
    # Tablas de dimensiones
    sub_t = st.tabs(["Consultas", "Páginas", "Países", "Dispositivos"])
    with sub_t[0]:
        st.dataframe(df_p.groupby('Query').agg({'Clicks':'sum','Impresiones':'sum','Posicion':'mean'}).sort_values('Clicks', ascending=False).style.format(precision=2), use_container_width=True)
    with sub_t[1]:
        df_p['Página'] = "/" + df_p['Query'].str.replace(" ", "-")
        st.dataframe(df_p.groupby('Página').agg({'Clicks':'sum','Impresiones':'sum'}).sort_values('Clicks', ascending=False), use_container_width=True)

with tab_idx:
    st.subheader("Estado de Cobertura")
    v_now, e_now = df_i.iloc[-1]['Validas'], df_i.iloc[-1]['Errores']
    ci1, ci2 = st.columns(2)
    ci1.metric("Páginas Válidas", f"{v_now:,}")
    ci2.metric("Páginas con Error", f"{e_now:,}", delta_color="inverse")

    
    st.plotly_chart(px.area(df_i, x='Fecha', y=['Validas', 'Errores'], color_discrete_map={'Validas':'#34A853', 'Errores':'#D93025'}, line_shape='hv', template="none"), use_container_width=True)

with tab_teacher:
    st.header("Benchmarks y Guía del Taller")
    
    st.subheader("📌 Valores de Referencia (¿Qué es normal?)")
    st.table(pd.DataFrame({
        "Sector": ["Ecommerce", "Informativo/Blog", "Nicho/Marca"],
        "CTR Saludable": ["2% - 5%", "0.8% - 2%", "10% - 25%"],
        "Notas": ["Afectado por Shopping y Ads", "Mucho tráfico 'curioso'", "Alta intención/Fidelidad"]
    }))
    
    st.divider()
    st.subheader("📝 Guía del Escenario")
    guides = {
        "Sitio 1: Ecommerce (Caída Técnica)": "Crisis total: Caída de impresiones + clics = Problema técnico de indexación.",
        "Sitio 2: Blog (Problema de CTR)": "Crisis de Snippet: Muchas impresiones + CTR < 1% = Títulos no atractivos.",
        "Sitio 3: Nicho Dev (Oportunidad)": "Oro puro: CTR alto + pocas impresiones = Necesidad de escalar volumen."
    }
    st.info(guides[sc_name])

st.sidebar.divider()
st.sidebar.download_button("📥 Exportar CSV", df_p.to_csv(index=False), "gsc_lab_data.csv")
