import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="GSC Educational Simulator", layout="wide", page_icon="📈")

# Estilo para tarjetas de métricas
st.markdown("""
    <style>
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- GENERADOR DE DATOS REALISTAS ---
def generate_realistic_data(scenario):
    end_date = datetime.now()
    dates = pd.date_range(end=end_date, periods=180) # 6 meses como pediste
    
    # Diccionarios de Queries Verosímiles
    queries_dict = {
        "Sitio 1: Ecommerce en Caída": [
            "comprar zapatillas running", "zapatillas nike baratas", "tienda deportes online",
            "mejores botas montaña", "calzado deportivo mujer", "ofertas zapatillas running",
            "zapatillas para maratón", "zapatos trekking impermeables", "outlet deportes"
        ],
        "Sitio 2: Blog con Bajo CTR": [
            "cómo bajar de peso rápido", "dieta cetogénica menú", "ejercicios en casa",
            "beneficios del ayuno intermitente", "mejores proteínas fitness", "cómo marcar abdominales",
            "rutina cardio 20 min", "alimentos con magnesio", "qué comer antes de entrenar"
        ],
        "Sitio 3: Nicho Oportunidad": [
            "mejor ratón ergonómico para túnel carpiano 2026", "teclado mecánico silencioso oficina",
            "mx master 3 vs mx anywhere 3", "mejor silla ergonómica teletrabajo",
            "configuración setup productivo 2026", "ratón vertical opiniones", "reposapiés oficina ergonómico"
        ]
    }
    
    countries = ["España", "México", "Argentina", "Colombia", "Chile", "EE.UU (Hispanos)"]
    devices = ["Mobile", "Desktop", "Tablet"]
    current_queries = queries_dict.get(scenario)
    
    data = []
    for date in dates:
        # Simulación de estacionalidad o eventos
        is_drop = (scenario == "Sitio 1: Ecommerce en Caída" and date > dates[120])
        
        for q in current_queries:
            # Asignar una "importancia" fija a la query para que no sea aleatorio puro
            query_weight = np.random.uniform(0.5, 2.0)
            
            for country in countries:
                # El tráfico móvil suele ser mayor (60-70%)
                for device in devices:
                    dev_mod = 1.2 if device == "Mobile" else (0.8 if device == "Desktop" else 0.2)
                    
                    if scenario == "Sitio 1: Ecommerce en Caída":
                        base_imp = 500 * query_weight
                        if is_drop:
                            imp = base_imp * 0.7
                            clicks = np.random.randint(0, 2)
                            pos = np.random.uniform(15, 40)
                        else:
                            imp = base_imp
                            clicks = int(imp * np.random.uniform(0.05, 0.12) * dev_mod)
                            pos = np.random.uniform(1.2, 5.0)
                    
                    elif scenario == "Sitio 2: Blog con Bajo CTR":
                        imp = 2000 * query_weight
                        clicks = int(imp * np.random.uniform(0.001, 0.008)) # CTR muy bajo < 1%
                        pos = np.random.uniform(1.1, 3.5)
                    
                    else: # Nicho Oportunidad
                        imp = 50 * query_weight
                        clicks = int(imp * np.random.uniform(0.15, 0.30) * dev_mod) # CTR muy alto
                        pos = np.random.uniform(1.0, 2.5)
                    
                    data.append([date, q, country, device, max(0, clicks), max(1, int(imp)), pos])
            
    df = pd.DataFrame(data, columns=['Fecha', 'Query', 'Pais', 'Dispositivo', 'Clicks', 'Impresiones', 'Posicion'])
    df['CTR'] = (df['Clicks'] / df['Impresiones']) * 100
    return df

# --- INTERFAZ ---
st.sidebar.title("🛠️ GSC Simulator Admin")
option = st.sidebar.radio("Modo de datos:", ["Escenarios de Clase", "Cargar CSV"])

if option == "Escenarios de Clase":
    sc = st.sidebar.selectbox("Seleccionar Caso:", ["Sitio 1: Ecommerce en Caída", "Sitio 2: Blog con Bajo CTR", "Sitio 3: Nicho Oportunidad"])
    df = generate_realistic_data(sc)
else:
    up = st.sidebar.file_uploader("Subir datos de GSC (CSV)")
    if up: df = pd.read_csv(up, parse_dates=['Fecha'])
    else: 
        df = generate_realistic_data("Sitio 1: Ecommerce en Caída")
        st.info("Mostrando datos demo hasta que subas un archivo.")

# --- DASHBOARD ---
st.title("📈 Google Search Console Simulator")
st.caption("Herramienta de aprendizaje para analistas SEO")

# Métricas Principales
c1, c2, c3, c4 = st.columns(4)
total_clicks = df['Clicks'].sum()
total_imp = df['Impresiones'].sum()
c1.metric("Total Clicks", f"{total_clicks:,}")
c2.metric("Total Impresiones", f"{total_imp:,}")
c3.metric("CTR Medio", f"{(total_clicks/total_imp)*100:.2f}%")
c4.metric("Posición Media", f"{df['Posicion'].mean():.1f}")

# Gráfico Principal
st.subheader("Rendimiento")
chart_data = df.groupby('Fecha').agg({'Clicks':'sum', 'Impresiones':'sum'}).reset_index()
fig = px.line(chart_data, x='Fecha', y=['Clicks', 'Impresiones'], 
              color_discrete_map={'Clicks':'#4285F4', 'Impresiones':'#EA4335'},
              template="plotly_white")
st.plotly_chart(fig, use_container_width=True)

# --- SECCIÓN EDUCATIVA ---
st.divider()
st.header("🕵️ Auditoría Automática")
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Análisis de Queries")
    # Identificar Queries con "Umbral de Optimización"
    q_analysis = df.groupby('Query').agg({'Clicks':'sum', 'Impresiones':'sum', 'CTR':'mean', 'Posicion':'mean'}).reset_index()
    
    # Lógica: Posición buena (top 5) pero CTR malo (< 2%)
    opps = q_analysis[(q_analysis['Posicion'] < 5) & (q_analysis['CTR'] < 2)].sort_values('Impresiones', ascending=False)
    
    if not opps.empty:
        st.warning(f"Se encontraron {len(opps)} keywords con problemas de CTR.")
        st.write("Estas keywords están en página 1, pero los usuarios no hacen clic. **Acción:** Mejorar Titles y Meta Descriptions.")
        st.dataframe(opps[['Query', 'Impresiones', 'CTR', 'Posicion']].head(5), hide_index=True)
    else:
        st.success("No se detectan problemas críticos de CTR en el Top 10.")

with col_right:
    st.subheader("Salud del Sitio")
    last_30 = chart_data.tail(30)['Clicks'].mean()
    prev_30 = chart_data.iloc[-60:-30]['Clicks'].mean()
    
    diff = ((last_30 - prev_30) / prev_30) * 100
    if diff < -20:
        st.error(f"Caída detectada: {diff:.1f}% de clicks vs mes anterior.")
        st.write("**Hipótesis:** Revisa si hubo un Google Core Update o si se han desindexado URLs clave.")
    else:
        st.success(f"Tendencia estable: {diff:+.1f}% de variación mensual.")

# --- TABS DE SEGMENTACIÓN ---
st.divider()
t1, t2, t3 = st.tabs(["🔍 Consultas", "🌍 Países", "📱 Dispositivos"])

with t1:
    st.dataframe(q_analysis.sort_values('Clicks', ascending=False), use_container_width=True)

with t2:
    p_analysis = df.groupby('Pais').agg({'Clicks':'sum', 'Impresiones':'sum', 'CTR':'mean'}).sort_values('Clicks', ascending=False)
    st.bar_chart(p_analysis['Clicks'])

with t3:
    d_analysis = df.groupby('Dispositivo').agg({'Clicks':'sum', 'Impresiones':'sum', 'CTR':'mean'})
    st.table(d_analysis)

st.sidebar.markdown("---")
st.sidebar.write("📌 **Tip para alumnos:** Filtra por 'Mobile' para ver si la posición media cae respecto a Desktop. Eso indica problemas de usabilidad móvil.")
