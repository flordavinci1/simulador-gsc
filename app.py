import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="GSC Pro Simulator", layout="wide", page_icon="🎯")

# --- GENERADOR DE DATOS REALISTAS ---
@st.cache_data
def generate_all_data(scenario):
    end_date = datetime.now()
    dates = pd.date_range(end=end_date, periods=180)
    
    # 1. DATOS DE RENDIMIENTO (Igual que antes pero optimizado)
    queries_dict = {
        "Sitio 1: Ecommerce de Tecnología (Caída)": ["comprar laptop", "teclados mecanicos", "monitores 4k", "graficas rtx", "tienda pc"],
        "Sitio 2: Blog de Ciberseguridad (Bajo CTR)": ["que es ddos", "phishing ejemplos", "encriptacion simetrica", "seguridad wifi", "antivirus"],
        "Sitio 3: Nicho Software Dev (Oportunidad)": ["configurar neovim python", "rust vs go backend", "docker raspberry pi", "setup dev 2026"]
    }
    
    perf_data = []
    current_queries = queries_dict.get(scenario)
    for date in dates:
        is_drop = (scenario == "Sitio 1: Ecommerce de Tecnología (Caída)" and date > dates[120])
        for q in current_queries:
            imp = np.random.randint(800, 1200) if scenario != "Sitio 3" else np.random.randint(50, 100)
            if is_drop:
                clicks, pos = np.random.randint(0, 2), np.random.uniform(20, 50)
            else:
                ctr_base = 0.08 if scenario != "Sitio 2" else 0.005
                clicks = int(imp * np.random.uniform(ctr_base, ctr_base+0.05))
                pos = np.random.uniform(1.2, 5.0)
            perf_data.append([date, q, clicks, imp, pos])
    
    df_perf = pd.DataFrame(perf_data, columns=['Fecha', 'Query', 'Clicks', 'Impresiones', 'Posicion'])
    df_perf['CTR'] = (df_perf['Clicks'] / df_perf['Impresiones']) * 100

    # 2. DATOS DE INDEXACIÓN (Nueva lógica)
    index_data = []
    for date in dates:
        if scenario == "Sitio 1: Ecommerce de Tecnología (Caída)" and date > dates[120]:
            # Simular desindexación masiva o errores 404
            validas = 500 - ( (date - dates[120]).days * 10 )
            errores = 10 + ( (date - dates[120]).days * 8 )
        elif scenario == "Sitio 2: Blog de Ciberseguridad (Bajo CTR)":
            validas, errores = 1200, 5
        else: # Nicho
            validas, errores = 45, 0
            
        index_data.append([date, max(0, int(validas)), int(errores)])
    
    df_index = pd.DataFrame(index_data, columns=['Fecha', 'Paginas_Validas', 'Errores'])
    
    return df_perf, df_index

# --- INTERFAZ ---
st.title("🎯 GSC Educational Simulator Pro")
st.sidebar.title("Configuración")

sc = st.sidebar.selectbox("Seleccionar Escenario:", [
    "Sitio 1: Ecommerce de Tecnología (Caída)", 
    "Sitio 2: Blog de Ciberseguridad (Bajo CTR)", 
    "Sitio 3: Nicho Software Dev (Oportunidad)"
])

df_perf, df_index = generate_all_data(sc)

# TABS PRINCIPALES (Estilo GSC)
tab_main_perf, tab_main_index = st.tabs(["📊 Rendimiento", "🔍 Indexación de Páginas"])

# --- TAB DE RENDIMIENTO ---
with tab_main_perf:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Clicks", f"{df_perf['Clicks'].sum():,}")
    c2.metric("Total Impresiones", f"{df_perf['Impresiones'].sum():,}")
    c3.metric("CTR Medio", f"{(df_perf['Clicks'].sum()/df_perf['Impresiones'].sum())*100:.2f}%")
    c4.metric("Posición Media", f"{df_perf['Posicion'].mean():.1f}")

    fig_perf = px.line(df_perf.groupby('Fecha').sum().reset_index(), x='Fecha', y=['Clicks', 'Impresiones'], 
                      title="Evolución de Rendimiento", color_discrete_map={'Clicks':'#4285F4', 'Impresiones':'#EA4335'})
    st.plotly_chart(fig_perf, use_container_width=True)
    
    st.subheader("Análisis de Consultas")
    st.dataframe(df_perf.groupby('Query').agg({'Clicks':'sum', 'Impresiones':'sum', 'CTR':'mean', 'Posicion':'mean'}).sort_values('Clicks', ascending=False), use_container_width=True)

# --- TAB DE INDEXACIÓN ---
with tab_main_index:
    st.header("Estado de la indexación")
    
    # KPIs de Indexación
    current_valid = df_index.iloc[-1]['Paginas_Validas']
    current_error = df_index.iloc[-1]['Errores']
    
    col_i1, col_i2 = st.columns(2)
    col_i1.metric("Páginas Indexadas (Válidas)", current_valid, delta=int(current_valid - df_index.iloc[-7]['Paginas_Validas']))
    col_i2.metric("Páginas con Error", current_error, delta=int(current_error - df_index.iloc[-7]['Errores']), delta_color="inverse")

    # Gráfico de Indexación
    fig_index = px.area(df_index, x='Fecha', y=['Paginas_Validas', 'Errores'], 
                        title="Estado de indexación a lo largo del tiempo",
                        color_discrete_map={'Paginas_Validas': '#34A853', 'Errores': '#D93025'},
                        line_shape='hv') # Estilo escalonado típico de GSC
    st.plotly_chart(fig_index, use_container_width=True)

    # Diagnóstico Educativo de Indexación
    st.divider()
    st.subheader("🕵️ Diagnóstico Técnico")
    if current_error > 20:
        st.error(f"Se han detectado {current_error} errores de indexación. Esto coincide con la caída de tráfico observada.")
        st.info("**Concepto Educativo:** Cuando las páginas válidas caen y los errores suben, Google deja de mostrar tu sitio. Esto puede ser por errores 404 tras una migración o bloqueos en el robots.txt.")
    elif current_valid < 50 and sc == "Sitio 3: Nicho Software Dev (Oportunidad)":
        st.success("Sitio pequeño y limpio. Todas las páginas enviadas están indexadas.")
        st.write("**Tip:** En sitios pequeños, cada página cuenta. Asegúrate de que el 'crawl budget' no se desperdicie.")
    else:
        st.success("La indexación se mantiene estable.")

# --- BARRA LATERAL (Download) ---
st.sidebar.divider()
csv_perf = df_perf.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("📥 Descargar Rendimiento (CSV)", csv_perf, "rendimiento.csv", "text/csv")
