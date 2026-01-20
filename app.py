import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="GSC Educational Simulator", layout="wide", page_icon="📈")

# Estilo CSS para mejorar la estética
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; border: 1px solid #e0e0e0; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_index=True)

# --- GENERADOR DE DATOS AVANZADO ---
def generate_data(scenario):
    dates = pd.date_range(end=pd.Timestamp.now(), periods=180)
    queries = {
        "Sitio 1: Ecommerce en Caída": ["comprar zapatos", "zapatillas running", "botas cuero"],
        "Sitio 2: Blog con Bajo CTR": ["recetas faciles", "como cocinar pasta", "cenas rapidas"],
        "Sitio 3: Nicho Oportunidad": ["mejor teclado mecanico 2024", "teclado gaming barato"]
    }
    countries = ["España", "México", "Argentina", "Colombia", "Chile"]
    devices = ["Mobile", "Desktop", "Tablet"]
    
    current_queries = queries.get(scenario, ["query dummy"])
    data = []

    for date in dates:
        # Lógica de impacto según escenario
        is_second_half = date > dates[90]
        
        for q in current_queries:
            for country in countries:
                for device in devices:
                    if scenario == "Sitio 1: Ecommerce en Caída":
                        # Caída fuerte de clicks a mitad del tiempo
                        base_imp = 200
                        base_clicks = 40 if not is_second_half else 2
                        pos = 3.2 if not is_second_half else 18.5
                    elif scenario == "Sitio 2: Blog con Bajo CTR":
                        # Mucha impresión, casi nada de clicks
                        base_imp = 1000
                        base_clicks = 1
                        pos = 2.1
                    else: # Nicho
                        base_imp = 20
                        base_clicks = 8
                        pos = 1.1
                    
                    # Añadir ruido aleatorio
                    imp = max(1, base_imp + np.random.randint(-10, 10))
                    clicks = max(0, base_clicks + np.random.randint(-2, 3))
                    
                    data.append([date, q, country, device, clicks, imp, pos])
            
    df = pd.DataFrame(data, columns=['Fecha', 'Query', 'Pais', 'Dispositivo', 'Clicks', 'Impresiones', 'Posicion'])
    df['CTR'] = (df['Clicks'] / df['Impresiones']) * 100
    return df

# --- SIDEBAR: CONTROL DE DATOS ---
st.sidebar.title("🎛️ Panel de Control")
source = st.sidebar.radio("Fuente de datos:", ["Escenarios Educativos", "Subir CSV Propio"])

if source == "Escenarios Educativos":
    escenario_nombre = st.sidebar.selectbox("Selecciona un caso de estudio:", 
                                            ["Sitio 1: Ecommerce en Caída", 
                                             "Sitio 2: Blog con Bajo CTR", 
                                             "Sitio 3: Nicho Oportunidad"])
    df = generate_data(escenario_nombre)
    st.sidebar.success(f"Analizando: {escenario_nombre}")
else:
    uploaded_file = st.sidebar.file_uploader("Sube tu CSV (Columnas: Fecha, Query, Pais, Dispositivo, Clicks, Impresiones, Posicion)")
    if uploaded_file:
        df = pd.read_csv(uploaded_file, parse_dates=['Fecha'])
    else:
        st.info("Esperando archivo... Mientras tanto, puedes explorar los escenarios.")
        df = generate_data("Sitio 1: Ecommerce en Caída")

# --- FILTROS GLOBALES ---
st.sidebar.divider()
st.sidebar.subheader("Filtros de Vista")
selected_device = st.sidebar.multiselect("Dispositivo", df['Dispositivo'].unique(), default=df['Dispositivo'].unique())
df_filtered = df[df['Dispositivo'].isin(selected_device)]

# --- MAIN DASHBOARD ---
st.title("📊 GSC Simulator MVP")

# KPIs
c1, c2, c3, c4 = st.columns(4)
total_c = df_filtered['Clicks'].sum()
total_i = df_filtered['Impresiones'].sum()
avg_ctr = (total_c / total_i) * 100
avg_pos = df_filtered['Posicion'].mean()

c1.metric("Total Clicks", f"{total_c:,}")
c2.metric("Total Impresiones", f"{total_i:,}")
c3.metric("CTR Medio", f"{avg_ctr:.2f}%")
c4.metric("Posición Media", f"{avg_pos:.1f}")

# Gráfico de Tendencia
st.subheader("Rendimiento en el tiempo")
trend = df_filtered.groupby('Fecha').agg({'Clicks':'sum', 'Impresiones':'sum'}).reset_index()
fig = px.line(trend, x='Fecha', y=['Clicks', 'Impresiones'], color_discrete_sequence=['#4285F4', '#EA4335'])
st.plotly_chart(fig, use_container_width=True)

# --- CAPA EDUCATIVA: INSIGHTS AUTOMÁTICOS ---
st.divider()
st.subheader("💡 Auditoría SEO Automática")

col_ins_1, col_ins_2 = st.columns(2)

with col_ins_1:
    # Análisis de Caída
    recent = trend.tail(14)['Clicks'].sum()
    previous = trend.iloc[-28:-14]['Clicks'].sum()
    if recent < previous * 0.7:
        st.error(f"⚠️ **ALERTA DE CAÍDA:** El tráfico cayó un {((1 - recent/previous)*100):.1f}% en los últimos 14 días.")
        st.write("Explicación: Esto suele deberse a problemas técnicos (indexación) o penalizaciones.")
    else:
        st.success("✅ Estabilidad de tráfico detectada.")

with col_ins_2:
    # Análisis de CTR
    queries_bad_ctr = df_filtered.groupby('Query').agg({'CTR':'mean', 'Impresiones':'sum'}).query('CTR < 1 and Impresiones > 500')
    if not queries_bad_ctr.empty:
        st.warning(f"⚠️ **BAJO CTR:** Tienes {len(queries_bad_ctr)} queries con muchas impresiones pero pocos clicks.")
        st.write("Explicación: Revisa tus títulos (Titles). No están siendo atractivos para el usuario.")

# --- TABS DE DATOS ---
st.divider()
tab1, tab2, tab3 = st.tabs(["🔍 Consultas (Queries)", "🌍 Países", "📱 Dispositivos"])

with tab1:
    q_df = df_filtered.groupby('Query').agg({'Clicks':'sum', 'Impresiones':'sum', 'CTR':'mean', 'Posicion':'mean'}).sort_values('Clicks', ascending=False)
    st.dataframe(q_df.style.format(precision=2), use_container_width=True)

with tab2:
    p_df = df_filtered.groupby('Pais').agg({'Clicks':'sum', 'Impresiones':'sum', 'CTR':'mean'}).sort_values('Clicks', ascending=False)
    fig_pais = px.bar(p_df.reset_index(), x='Pais', y='Clicks', color='Pais')
    st.plotly_chart(fig_pais)

with tab3:
    d_df = df_filtered.groupby('Dispositivo').agg({'Clicks':'sum', 'Impresiones':'sum', 'CTR':'mean'})
    st.table(d_df)
