# Añadir este bloque dentro de la pestaña "Libro del Profesor" (tab_teacher)
with tab_teacher:
    st.markdown("---")
    st.subheader("🌲 Árbol de Decisión SEO")
    st.write("Sigue este flujo para diagnosticar la caída de este escenario:")
    
    with st.expander("1. ¿Es un problema externo?"):
        st.write("- **Estacionalidad:** Revisa Google Trends.")
        st.write("- **Coyuntura:** ¿Hay factores externos que afecten la demanda?")
        
    with st.expander("2. ¿Es una caída GLOBAL? (Mira el gráfico de Cobertura)"):
        st.write("- **Bloqueo técnico:** Revisa Robots.txt o meta-tags 'noindex'.")
        st.write("- **Servidor:** ¿Hay un aumento masivo de errores 5xx o 404?")
        
    with st.expander("3. ¿Es una caída PUNTUAL? (Mira la tabla de Páginas)"):
        st.write("- **Canibalización:** ¿Hay dos URLs compitiendo por la misma Query?")
        st.write("- **Cambio de contenido:** ¿Se editó la URL recientemente?")
        st.write("- **Páginas Huérfanas:** ¿Sigue teniendo enlaces internos?")
