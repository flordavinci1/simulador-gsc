import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="GSC Lab: Decision Tree SEO", layout="wide", page_icon="🧪")

# --- 2. GENERADOR DE DATOS (Lógica de Árbol de Decisión) ---
@st.cache_data
def get_data(scenario_name):
    dates = pd.date_range(end=datetime.now(), periods=180)
    
    queries_config = {
        "Sitio 1: Ecommerce (Caída Técnica Global)": {"comprar laptop": 0.6, "pc gaming": 0.25, "monitor 4k": 0.15},
        "Sitio 2: Blog (Bajo CTR / Contenido)": {"que es ddos": 0.5, "phishing ejemplos": 0.3, "seguridad wifi": 0.2},
        "Sitio 3: Nicho Dev (Puntual / Canibalización)": {"configurar neovim": 0.7, "rust vs go": 0.3}
    }
    
    perf_list = []
    current_qs = queries_config.get(scenario_name, {"query": 1.0})
    
    for date in dates:
        # Escenario 1: Caída Técnica (Día 120+) -> Caen Clicks e Impresiones
        is_drop_global = (scenario_name == "Sitio 1: Ecommerce (Caída Técnica Global)" and date > dates[120])
        # Escenario 3: Caída Puntual (Día 140+) -> Solo cae una query por "Canibalización"
        
        tech_visibility = 0.05 if is_drop_global else 1.0
        
        for q, weight in current_qs.items():
            base_imp = 4000 * weight if "Nicho" not in scenario_name else 300 * weight
            
            # Lógica de Canibalización para Escenario 3
            if scenario_name == "Sitio 3: Nicho Dev (Puntual / Canibalización)" and q == "configurar neovim" and date > dates[140]:
                imp = int(base_imp * 0.3) # Cae solo esta query
                pos = 12.0
            else:
                imp = int((base_imp + np.random.normal(0, base_imp * 0.1)) * tech_visibility)
                pos = np.random.uniform(1.1, 3.5) if not is_drop_global else np.random.uniform(50, 80)

            ctr = 0.005 if scenario_name == "Sitio 2: Blog (Bajo CTR / Contenido)" else 0.03
            if is_drop_global: ctr = 0.001
            
            clicks = int(imp * ctr)
            perf_list.append([date, q, clicks, imp, pos])
            
    df_perf = pd.DataFrame(perf_list, columns=['Fecha', 'Query', 'Clicks', 'Impresiones', 'Posicion'])
    
    # Lógica de Indexación (Relacionada al Árbol)
    idx_list = []
    for date in dates:
        if scenario_name == "Sitio 1: Ecommerce (Caída Técnica Global)" and date > dates[120]:
            v, e = max(0, 800 - ((date - dates[120]).days * 25)), 10 + ((date - dates[120]).days * 20)
        else:
            v, e = 1000, 5
        idx_list.append([date, int(v), int(e)])
        
    return df_perf, pd.DataFrame(idx_list, columns=['Fecha', 'Validas', 'Errores'])

# --- 3. INTERFAZ Y NAVEGACIÓN ---
st.sidebar.title("🧪 GSC Workshop v3.3")
sc_name = st.sidebar.selectbox("Escenario para el taller:", 
    ["Sitio 1: Ecommerce (Caída Técnica Global)", 
     "Sitio 2: Blog (Bajo CTR / Contenido)", 
     "Sitio 3: Nicho Dev (Puntual / Canibalización)"])

time_range = st.sidebar.selectbox("Periodo de análisis:", ["Últimos 28 días", "Últimos 3 meses", "Últimos 6 meses"])

# Filtro de tiempo
days_map = {"Últimos 28 días": 28, "Últimos 3 meses": 90, "Últimos 6 meses": 180}
cutoff = datetime.now() - timedelta(days=days_map[time_range])
df_p_raw, df_i_raw = get_data(sc_name)
df_p = df_p_raw[df_p_raw['Fecha'] >= cutoff]
df_i = df_i_raw[df_i_raw['Fecha'] >= cutoff]

# --- 4. TABS (ORDEN CORRECTO) ---
tab_perf, tab_idx, tab_teacher = st.tabs(["📊 Rendimiento", "🔍 Indexación", "🌳 Árbol de Decisión"])

with tab_perf:
    st.subheader(f"Dashboard de Rendimiento ({time_range})")
    c1, c2, c3, c4 = st.columns(4)
    tc, ti = df_p['Clicks'].sum(), df_p['Impresiones'].sum()
    c1.metric("Clics", f"{tc:,}")
    c2.metric("Impresiones", f"{ti:,}")
    c3.metric("CTR Medio", f"{(tc/ti)*100:.2f}%")
    c4.metric("Posición Media", f"{df_p['Posicion'].mean():.1f}")
    
    st.plotly_chart(px.line(df_p.groupby('Fecha').sum().reset_index(), x='Fecha', y=['Clicks', 'Impresiones'], 
                           color_discrete_map={'Clicks': '#4285F4', 'Impresiones': '#7E3FF2'},
                           template="none"), use_container_width=True)
    
    st.divider()
    st.subheader("Tabla de Consultas")
    st.dataframe(df_p.groupby('Query').agg({'Clicks':'sum','Impresiones':'sum','Posicion':'mean'}).sort_values('Clicks', ascending=False).style.format(precision=2), use_container_width=True)

with tab_idx:
    st.subheader("Estado de Cobertura técnica")
    st.plotly_chart(px.area(df_i, x='Fecha', y=['Validas', 'Errores'], color_discrete_map={'Validas':'#34A853', 'Errores':'#D93025'}, line_shape='hv', template="none"), use_container_width=True)

with tab_teacher:
    st.header("Guía del Taller: Árbol de Decisión SEO")
    st.write("Usa este esquema para que los alumnos diagnostiquen la caída:")
    
    # Representación visual del flujo de pensamiento
    

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.info("### Paso 1: Filtro Externo\n¿Es estacional o coyuntural? (Comparar con histórico o Trends)")
        st.warning("### Paso 2: Gravedad\n¿Es una caída GLOBAL o PUNTUAL?")
    
    with col_t2:
        st.success("### Paso 3: Origen\n- Global: Indexación (Robots, 404 masivos).\n- Puntual: Canibalización, 404 de URL o cambio de contenido.")

    st.divider()
    st.subheader("💡 Solución del Escenario Seleccionado")
    if "Global" in sc_name:
        st.error("**DIAGNÓSTICO:** Caída Técnica Global. Clics e impresiones caen a la vez porque las páginas válidas en Cobertura desaparecieron.")
    elif "Bajo CTR" in sc_name:
        st.warning("**DIAGNÓSTICO:** Problema de Contenido/CTR. Las impresiones se mantienen pero los clics son bajos. El 'Snippet' no atrae.")
    else:
        st.success("**DIAGNÓSTICO:** Caída Puntual. Una sola URL cayó (Canibalización). Google prefiere otra página para esa consulta.")

st.sidebar.divider()
st.sidebar.download_button("📥 Exportar CSV para clase", df_p.to_csv(index=False), "datos_taller_seo.csv")
