import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="GSC Educational Simulator", layout="wide", page_icon="📈")

# Estilo CSS para mejorar la estética de las métricas
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- GENERADOR DE DATOS INTERNO ---
def generate_data(scenario):
    end_date = datetime.now()
    dates = pd.date_range(end=end_date, periods=90) # 3 meses de datos para que sea legible
    
    queries_dict = {
        "Sitio 1: Ecommerce en Caída": ["comprar zapatos", "zapatillas running", "ofertas moda"],
        "Sitio 2: Blog con Bajo CTR": ["como hacer cafe", "receta pan casero", "trucos cocina"],
        "Sitio 3: Nicho Oportunidad": ["mejor teclado ergonomico 2026", "teclado mecanico barato"]
    }
    
    countries = ["España", "México", "Argentina", "Colombia", "Chile"]
    devices = ["Mobile", "Desktop", "Tablet"]
    current_queries = queries_dict.get(scenario)
    
    data = []
    for date in dates:
        # Lógica de impacto: caída a mitad del periodo para el escenario 1
        is_drop_period = (scenario == "Sitio 1: Ecommerce en Caída" and date > dates[45])
        
        for q in current_queries:
            for country in countries:
                for device in devices:
                    if scenario == "Sitio 1: Ecommerce en Caída":
                        imp = np.random.randint(100, 150)
                        clicks = np.random.randint(10, 20) if not is_drop_period else np.random.randint(0, 3)
                        pos = np.random.uniform(2, 4) if not is_drop_period else np.random.uniform(15, 25)
                    
                    elif scenario == "Sitio 2: Blog con Bajo CTR":
                        imp = np.random.randint(1000, 2000) # Muchas impresiones
                        clicks = np.random.randint(0, 5)    # Pero poquísimos clicks
                        pos = np.random.uniform(1.5, 3.0)
                    
                    else: # Nicho Oportunidad
                        imp = np.random.randint(10, 30)    # Poco volumen
                        clicks = np.random.randint(5, 12)   # Pero CTR muy alto
                        pos = np.random.uniform(1.0, 2.0)
                    
                    data.append([date, q, country, device, clicks, imp, pos])
            
    df = pd.DataFrame(data, columns=['Fecha', 'Query', 'Pais', 'Dispositivo', 'Clicks', 'Impresiones', 'Posicion'])
    df['CTR'] = (df['Clicks'] / df['Impresiones']) * 100
    return df

# --- INTERFAZ DE USUARIO (SIDEBAR) ---
st.sidebar.title("🚀 GSC Sim v1.0")
source = st.sidebar.radio("Fuente de datos:", ["Escenarios Educativos", "Subir CSV Propio"])

if source == "Escenarios Educativos":
    escenario_nombre = st.sidebar.selectbox("Selecciona un caso:", 
                                            ["Sitio 1: Ecommerce en Caída", 
                                             "Sitio 2: Blog con Bajo CTR", 
                                             "Sitio 3: Nicho Oportunidad"])
    df = generate_data(escenario_nombre)
    st.sidebar.info(f"Escenario activo: {escenario_nombre}")
else:
    uploaded_file = st.sidebar.file_uploader("Sube tu CSV")
    if uploaded_file:
        df = pd.read_csv(uploaded_file, parse_dates=['Fecha'])
    else:
        st.warning("Usando datos por defecto hasta que subas un archivo.")
        df = generate_data("Sitio 1: Ecommerce en Caída")

# Filtros rápidos
st.sidebar.divider()
f_device = st.sidebar.multiselect("Filtrar Dispositivo", df['Dispositivo'].unique(), default=df['Dispositivo'].unique())
df_filtered = df[df['Dispositivo'].isin(f_device)]

# --- DASHBOARD PRINCIPAL ---
st.title("🎓 Simulador de Search Console")
st.markdown("Herramienta educativa para diagnóstico de anomalías SEO.")

# KPIs Superiores
c1, c2, c3, c4 = st.columns(4)
total_clicks = df_filtered['Clicks'].sum()
total_imp = df_filtered['Impresiones'].sum()
avg_ctr = (total_clicks / total_imp) * 100
avg_pos = df_filtered['Posicion'].mean()

c1.metric("Clicks", f"{total_clicks:,}")
c2.metric("Impresiones", f"{total_imp:,}")
c3.metric("CTR Medio", f"{avg_ctr:.2f}%")
c4.metric("Posición Media", f"{avg_pos:.1f}")

# Gráfico de Líneas (Rendimiento)
st.subheader("Rendimiento en el tiempo")
trend_data = df_filtered.groupby('Fecha').agg({'Clicks':'sum', 'Impresiones':'sum'}).reset_index()
fig_line = px.line(trend_data, x='Fecha', y=['Clicks', 'Impresiones'], 
                  color_discrete_map={'Clicks': '#4285F4', 'Impresiones': '#EA4335'},
                  template="plotly_white")
st.plotly_chart(fig_line, use_container_width=True)

# --- PANEL DE INSIGHTS EDUCATIVOS ---
st.divider()
st.subheader("💡 Análisis del Consultor AI")
col_a, col_b = st.columns(2)

with col_a:
    # Diagnóstico de Tráfico
    recent_7d = trend_data.tail(7)['Clicks'].sum()
    prev_7d = trend_data.iloc[-14:-7]['Clicks'].sum()
    
    if recent_7d < prev_7d * 0.5:
        st.error("🆘 **ALERTA CRÍTICA:** Caída masiva de tráfico detectada. Revisa posibles errores de rastreo o pérdida de posiciones clave.")
    elif avg_ctr < 1.0:
        st.warning("⚠️ **AVISO DE CTR:** Tus impresiones son altas pero los clicks bajos. Considera optimizar los metatítulos.")
    else:
        st.success("✅ El patrón de tráfico parece saludable para este nicho.")

with col_b:
    # Diagnóstico de Dispositivos
    mobile_share = (df_filtered[df_filtered['Dispositivo'] == 'Mobile']['Clicks'].sum() / total_clicks) * 100
    st.info(f"📊 **Dato Clave:** El {mobile_share:.1f}% de tu tráfico es móvil. Asegúrate de que la velocidad de carga en celulares sea óptima.")

# --- TABLAS DETALLADAS ---
st.divider()
t_queries, t_countries, t_devices = st.tabs(["🔍 Queries", "🌍 Países", "📱 Dispositivos"])

with t_queries:
    q_table = df_filtered.groupby('Query').agg({
        'Clicks': 'sum', 
        'Impresiones': 'sum', 
        'CTR': 'mean', 
        'Posicion': 'mean'
    }).sort_values('Clicks', ascending=False)
    st.dataframe(q_table.style.format(precision=2), use_container_width=True)

with t_countries:
    p_table = df_filtered.groupby('Pais').agg({'Clicks': 'sum', 'Impresiones': 'sum', 'CTR': 'mean'}).sort_values('Clicks', ascending=False)
    fig_bar = px.bar(p_table.reset_index(), x='Pais', y='Clicks', title="Clicks por País", color_discrete_sequence=['#34A853'])
    st.plotly_chart(fig_bar)

with t_devices:
    d_table = df_filtered.groupby('Dispositivo').agg({'Clicks': 'sum', 'Impresiones': 'sum', 'CTR': 'mean'})
    st.table(d_table)

st.sidebar.caption("Desarrollado para fines educativos - MVP GSC")
