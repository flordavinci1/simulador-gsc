import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="GSC Pro Simulator", layout="wide")

# --- GENERADOR DE DATOS ---
@st.cache_data
def get_all_data(scenario):
    dates = pd.date_range(end=datetime.now(), periods=180)
    
    # Queries Verosímiles
    queries_map = {
        "Ecommerce (Caída Técnica)": ["comprar laptop", "teclado mecanico", "monitor 4k", "grafica rtx"],
        "Blog (Bajo CTR)": ["que es phishing", "ataque ddos", "encriptacion datos", "seguridad wifi"],
        "Nicho Dev (Oportunidad)": ["configurar neovim 2026", "rust vs go", "docker raspberry pi 5"]
    }
    
    q_list = queries_map.get(scenario, ["query dummy"])
    perf_list = []
    idx_list = []
    
    for date in dates:
        # Lógica Rendimiento
        is_drop = (scenario == "Ecommerce (Caída Técnica)" and date > dates[120])
        for q in q_list:
            imp = np.random.randint(1000, 1500) if scenario != "Nicho Dev (Oportunidad)" else np.random.randint(50, 100)
            if is_drop:
                clicks, pos = np.random.randint(0, 2), np.random.uniform(25, 45)
            elif scenario == "Blog (Bajo CTR)":
                clicks, pos = np.random.randint(1, 8), np.random.uniform(1.2, 3.5)
            else:
                clicks, pos = int(imp * np.random.uniform(0.15, 0.25)), np.random.uniform(1.1, 2.5)
            perf_list.append([date, q, clicks, imp, pos])
        
        # Lógica Indexación
        if is_drop:
            v, e = max(0, 500 - (date - dates[120]).days * 12), 5 + (date - dates[120]).days * 10
        else:
            v, e = (1200 if scenario == "Blog (Bajo CTR)" else 500), np.random.randint(0, 5)
        idx_list.append([date, v, e])
            
    return pd.DataFrame(perf_list, columns=['Fecha','Query','Clicks','Impresiones','Posicion']), \
           pd.DataFrame(idx_records, columns=['Fecha','Validas','Errores'])

# --- NAVEGACIÓN (SIDEBAR) ---
with st.sidebar:
    st.title("🧪 GSC Lab")
    menu = st.radio("Navegación", ["📈 Rendimiento", "🔍 Indexación", "👨‍🏫 Guía Estratégica", "📂 Cargar Datos"])
    st.divider()
    sc_choice = st.selectbox("Caso de Estudio:", ["Ecommerce (Caída Técnica)", "Blog (Bajo CTR)", "Nicho Dev (Oportunidad)"])
    
# Carga de datos base
df_p, df_i = get_all_data(sc_choice)
df_p['CTR'] = (df_p['Clicks'] / df_p['Impresiones']) * 100

# --- VISTA: RENDIMIENTO ---
if menu == "📈 Rendimiento":
    st.header(f"Rendimiento de búsqueda: {sc_choice}")
    
    # 1. KPIs Superiores
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Clics totales", f"{df_p['Clicks'].sum():,}")
    c2.metric("Impresiones totales", f"{df_p['Impresiones'].sum():,}")
    c3.metric("CTR medio", f"{(df_p['Clicks'].sum()/df_p['Impresiones'].sum())*100:.2f}%")
    c4.metric("Posición media", f"{df_p['Posicion'].mean():.1f}")

    # 2. Gráfico (Eilo GSC con doble eje)
    trend = df_p.groupby('Fecha').agg({'Clicks':'sum', 'Impresiones':'sum'}).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=trend['Fecha'], y=trend['Clicks'], name="Clics", line=dict(color='#4285F4', width=3)))
    fig.add_trace(go.Scatter(x=trend['Fecha'], y=trend['Impresiones'], name="Impresiones", line=dict(color='#7E3FF2', width=3), yaxis="y2"))
    
    fig.update_layout(
        template="none",
        hovermode="x unified",
        yaxis=dict(title="Clics", titlefont=dict(color="#4285F4"), tickfont=dict(color="#4285F4")),
        yaxis2=dict(title="Impresiones", titlefont=dict(color="#7E3FF2"), tickfont=dict(color="#7E3FF2"), overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

    # 3. Tablas Detalladas
    st.divider()
    t1, t2, t3, t4 = st.tabs(["CONSULTAS", "PÁGINAS", "PAÍSES", "DISPOSITIVOS"])
    
    with t1:
        q_table = df_p.groupby('Query').agg({'Clicks':'sum', 'Impresiones':'sum', 'CTR':'mean', 'Posicion':'mean'}).sort_values('Clicks', ascending=False)
        st.dataframe(q_table.style.format(precision=2), use_container_width=True)
    with t2:
        st.info("Simulación de páginas internas del sitio.")
        st.dataframe(df_p.groupby('Query').sum()[['Clicks', 'Impresiones']].head()) # Placeholder
    with t3:
        st.bar_chart(df_p.groupby('Query').sum()['Clicks']) # Placeholder para países

# --- VISTA: INDEXACIÓN ---
elif menu == "🔍 Indexación":
    st.header("Cobertura de Indexación")
    
    ci1, ci2 = st.columns(2)
    ci1.metric("Páginas Válidas", df_i.iloc[-1]['Validas'])
    ci2.metric("Páginas con Error", df_i.iloc[-1]['Errores'], delta_color="inverse")

    
    fig_i = px.area(df_i, x='Fecha', y=['Validas', 'Errores'], 
                    color_discrete_map={'Validas': '#34A853', 'Errores': '#EA4335'},
                    line_shape='hv', template="none")
    st.plotly_chart(fig_i, use_container_width=True)

# --- VISTA: ESTRATEGIA (RESUMEN PARA PROFES) ---
elif menu == "👨‍🏫 Guía Estratégica":
    st.header("Resumen Diagnóstico para el Docente")
    
    st.subheader(f"Análisis del caso: {sc_choice}")
    if "Ecommerce" in sc_choice:
        st.error("📉 **PROBLEMA:** Desplome técnico.")
        st.markdown("""
        - **Observación:** Las impresiones caen ligeramente pero los clics desaparecen.
        - **Causa en Indexación:** Las páginas válidas bajaron de 500 a casi 0.
        - **Acción:** Revisar redirecciones 301 o errores 5xx en el servidor.
        """)
    elif "Blog" in sc_choice:
        st.warning("🎯 **PROBLEMA:** Bajo CTR.")
        st.markdown("""
        - **Observación:** El sitio está en el Top 3 (Posición < 3) pero el CTR es menor al 1%.
        - **Acción:** Optimizar el Title y la Meta Description para generar curiosidad.
        """)
    else:
        st.success("💎 **PROBLEMA:** Falta de Escalabilidad.")
        st.markdown("""
        - **Observación:** Rendimiento perfecto pero bajo volumen.
        - **Acción:** Identificar temas 'Seed' con más volumen de búsqueda.
        """)

# --- VISTA: CARGAR DATOS ---
else:
    st.header("Subir Datos Dummy")
    st.write("Sube un CSV con: `Fecha, Query, Clicks, Impresiones, Posicion` para visualizarlo.")
    up = st.file_uploader("Cargar archivo")
    if up:
        st.success("Datos cargados. Revisa la pestaña de Rendimiento.")

# --- BOTÓN DESCARGA ---
st.sidebar.divider()
st.sidebar.download_button("📥 Bajar CSV actual", df_p.to_csv(index=False), "gsc_lab_data.csv")
