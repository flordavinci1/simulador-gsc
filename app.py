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
        is_drop = (scenario_name == "Sitio 1: Ecommerce (Caída Técnica)" and date > dates[120])
        tech_visibility = 0.05 if is_drop else 1.0
        
        for q, weight in current_qs.items():
            base_imp = 3000 * weight if scenario_name != "Sitio 3: Nicho Dev (Oportunidad)" else 200 * weight
            imp = int((base_imp + np.random.normal(0, base_imp * 0.1)) * tech_visibility)
            
            if is_drop:
                pos = np.random.uniform(40, 80)
                ctr = np.random.uniform(0.0005, 0.001) # Clicks casi nulos
            elif scenario_name == "Sitio 1: Ecommerce (Caída Técnica)":
                pos = np.random.uniform(3.0, 8.0)
                ctr = np.random.uniform(0.02, 0.045) # CTR REALISTA ECOMMERCE (2% - 4.5%)
            elif scenario_name == "Sitio 2: Blog (Problema de CTR)":
                pos = np.random.uniform(1.1, 2.5)
                ctr = np.random.uniform(0.004, 0.009) # CTR BAJO (Menos de 1%)
            else: # Nicho Dev
                pos = np.random.uniform(1.2, 2.2)
                ctr = np.random.uniform(0.08, 0.12) # CTR NICHO (8% - 12%)
            
            clicks = int(imp * ctr)
            perf_list.append([date, q, clicks, imp, pos, "México", "Mobile"])
            
    # (Resto del código de indexación igual...)
    return pd.DataFrame(perf_list, columns=['Fecha', 'Query', 'Clicks', 'Impresiones', 'Posicion', 'Pais', 'Dispositivo']), df_idx
