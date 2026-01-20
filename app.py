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
    idx_list = [] # Esta es la variable correcta
    
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
            
    # CORRECCIÓN AQUÍ: Cambiado idx_records por idx_list
    return pd.DataFrame(perf_records, columns=['Fecha','Query','Clicks','Impresiones','Posicion']) if 'perf_records' in locals() else pd.DataFrame(perf_list, columns=['Fecha','Query','Clicks','Impresiones','Posicion']), \
           pd.DataFrame(idx_list, columns=['Fecha','Validas','Errores'])

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
    total_c = df_p['Clicks'].sum()
    total_i = df_p['Impresiones'].sum()
    
    c1.metric("Clics totales", f"{total_c:,}")
    c2.metric("Impresiones totales", f"{total_i:,}")
    c3.metric("CTR medio", f"{(total_c/total_i)*100:.2f}%")
    c4.metric("Posición media", f"{df_p['Posicion'].mean():.1f}")

    # 2. Gráfico (Estilo GSC con doble eje)
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
        st.info("Páginas internas con mayor tráfico.")
        pages_df = df_p.copy()
        pages_df['Página'] = "/" + pages_df['Query'].str.replace(" ", "-")
        st.dataframe(pages_df.groupby('Página').sum()[['Clicks', 'Impresiones']].sort_values('Clicks', ascending=False))
    with t3:
        paises = pd.DataFrame({'País': ['España', 'México', 'Argentina', 'Colombia', 'Chile'], 'Clicks': [total_c*0.4, total_c*0.3, total_c*0.15, total_c*0.1, total_c*0.05]})
        st.bar_chart(paises.set_index('País'))

# --- VISTA: INDEXACIÓN ---
elif menu == "🔍 Indexación":
    st.header("Cobertura de Indexación")
    
    ci1, ci2 = st.columns(2)
    ci1.metric("Páginas Válidas", f"{int(df_i.iloc[-1]['Validas']):,}")
    ci2.metric("Páginas con Error", f"{int(df_i.iloc[-1]['Errores']):,}", delta_color="inverse")

    # Gráfico de área para indexación
    fig_i = px.area(df_i, x='Fecha', y=['Validas', 'Errores'], 
                    color_discrete_map={'Validas': '#34A853', 'Errores': '#EA4335'},
                    line_shape='hv', template="none")
    st.plotly_chart(fig_i, use_container_width=True)

# --- VISTA: ESTRATEGIA ---
elif menu == "👨‍🏫 Guía Estratégica":
    st.header("Análisis del Consultor SEO")
    
    if "Ecommerce" in sc_choice:
        st.error("📉 **DIAGNÓSTICO: Caída Técnica Crítica**")
        st.markdown("""
        - **Lo que vemos:** Una caída total de Clics a partir del cuarto mes.
        - **La causa:** Si miras la pestaña de **Indexación**, verás que las páginas válidas desaparecen. Esto no es un problema de contenido, es un problema de visibilidad técnica (posible error 500, robots.txt bloqueado o desindexación masiva).
        - **Tarea para el alumno:** ¿Qué harías primero? ¿Revisar el Search Console real o llamar al desarrollador?
        """)
    elif "Blog" in sc_choice:
        st.warning("🎯 **DIAGNÓSTICO: Problema de Atractivo (CTR)**")
        st.markdown("""
        - **Lo que vemos:** Posiciones excelentes (1.5 - 2.0) e Impresiones altas, pero poquísimos Clics.
        - **La causa:** El sitio es visible pero nadie quiere entrar. El "Snippet" es aburrido o no resuelve la duda.
        - **Tarea para el alumno:** Redactar un nuevo Meta Title y Description para la query principal.
        """)
    else:
        st.success("💎 **DIAGNÓSTICO: Potencial de Escalado**")
        st.markdown("""
        - **Lo que vemos:** Datos perfectos, CTR alto, pero volumen pequeño.
        - **La causa:** Estamos dominando un nicho muy pequeño.
        - **Tarea para el alumno:** Buscar 5 palabras clave de mayor volumen relacionadas para expandir el sitio.
        """)

# --- VISTA: CARGAR DATOS ---
else:
    st.header("Laboratorio de Datos Personalizado")
    st.write("Sube tu propio archivo CSV para analizarlo con esta interfaz.")
    up = st.file_uploader("Formato: Fecha, Query, Clicks, Impresiones, Posicion")
    if up:
        st.success("Datos cargados. Ve a Rendimiento para ver los gráficos.")

st.sidebar.divider()
st.sidebar.download_button("📥 Descargar Datos del Caso", df_p.to_csv(index=False), "gsc_lab_data.csv")
