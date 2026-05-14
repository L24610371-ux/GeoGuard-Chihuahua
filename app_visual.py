import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from math import radians, cos, sin, asin, sqrt
from datetime import datetime

# Importamos las funciones de la IA
from ia_helper import inicializar_ia, obtener_respuesta_ia

# ---------------------------------------------------------
# 1. CONFIGURACIÓN Y LLAVE
# ---------------------------------------------------------
st.set_page_config(page_title="GeoGuard - Chihuahua", layout="wide", page_icon="🛡️")

# PEGA TU API KEY AQUÍ
MI_API_KEY = "AIzaSyB5KosUMhYmE6TMmPSBYTAAH1oXHDFqXpQ" 

# ---------------------------------------------------------
# 2. FUNCIONES TÉCNICAS (MATEMÁTICAS Y DATOS)
# ---------------------------------------------------------
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371 # Radio de la Tierra en km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))

@st.cache_data
def cargar_datos():
    try:
        data = pd.read_csv('puntos_chihuahua.csv')
        data.columns = data.columns.str.strip()
        return data
    except:
        return pd.DataFrame()

# Estados de sesión para persistencia
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'reportes_comunidad' not in st.session_state:
    st.session_state.reportes_comunidad = []

df = cargar_datos()

# ---------------------------------------------------------
# 3. SIDEBAR (PANEL DE CONTROL Y ALERTAS REFINADAS)
# ---------------------------------------------------------
st.sidebar.title("🕹️ Panel de Control")

if not df.empty:
    municipio_sel = st.sidebar.selectbox("Filtrar por Ciudad:", ["Todos"] + sorted(df['municipio'].unique()))
    
    st.sidebar.divider()
    
    # REFINAMIENTO DE ALERTAS CIUDADANAS (PUNTO 2)
    st.sidebar.subheader("📢 Reporte de Sospecha")
    st.sidebar.caption("Tu reporte ayuda a mapear zonas de riesgo en tiempo real.")
    
    with st.sidebar.form("form_alerta", clear_on_submit=True):
        tipo_sospecha = st.selectbox("Incidente:", ["Persona sospechosa", "Falta de alumbrado", "Acoso", "Vehículo sospechoso", "Otro"])
        detalles = st.text_area("¿Qué observaste?", placeholder="Ej: Calle muy oscura cerca del parque...")
        btn_alerta = st.form_submit_button("Publicar Alerta Comunitaria")
        
        if btn_alerta:
            if detalles:
                # Ubicación ejemplo (Centro de Cuauhtémoc)
                nueva_alerta = {
                    "tipo": tipo_sospecha,
                    "nota": detalles,
                    "lat": 28.4044, "lon": -106.8664, 
                    "hora": datetime.now().strftime("%H:%M")
                }
                st.session_state.reportes_comunidad.append(nueva_alerta)
                st.sidebar.success("✅ Alerta publicada. ¡Gracias por colaborar con la seguridad de Chihuahua!")
            else:
                st.sidebar.error("Por favor, describe brevemente la situación.")

    st.sidebar.divider()
    
    # BUSCADOR DE PUNTO CERCANO
    if st.sidebar.button("🚨 Punto Seguro más Cercano"):
        u_lat, u_lon = 28.4110, -106.8620 # Ubicación usuario simulada
        df['distancia'] = df.apply(lambda r: calcular_distancia(u_lat, u_lon, r['Latitud'], r['Longitud']), axis=1)
        cercano = df.loc[df['distancia'].idxmin()]
        st.sidebar.warning(f"Refugio: {cercano['Nombre']}")
        st.sidebar.info(f"📞 Llama: {cercano['Telefono']}")
        centro_mapa, zoom_mapa = [cercano['Latitud'], cercano['Longitud']], 16
    else:
        centro_mapa, zoom_mapa = [28.633, -106.069], 8

    # ---------------------------------------------------------
    # 4. CUERPO PRINCIPAL (MAPA)
    # ---------------------------------------------------------
    st.title("🛡️ GeoGuard: Red de Seguridad Comunitaria")
    
    df_mapa = df[df['municipio'] == municipio_sel] if municipio_sel != "Todos" else df
    
    m = folium.Map(location=centro_mapa, zoom_start=zoom_mapa, tiles="cartodbpositron")
    cluster_refugios = MarkerCluster(name="Puntos Naranja").add_to(m)
    capa_alertas = folium.FeatureGroup(name="Alertas Rojas").add_to(m)

    # Marcadores Puntos Naranja
    for _, row in df_mapa.iterrows():
        popup_html = f"<b>{row['Nombre']}</b><br>{row['Direccion']}<br><a href='tel:{row['Telefono']}'>📞 Llamar</a>"
        folium.Marker(
            [row['Latitud'], row['Longitud']], 
            popup=popup_html, 
            icon=folium.Icon(color="orange", icon="shield", prefix="fa")
        ).add_to(cluster_refugios)

    # Marcadores de Alertas Ciudadanas
    for rep in st.session_state.reportes_comunidad:
        folium.Marker(
            [rep['lat'], rep['lon']],
            popup=f"⚠️ {rep['tipo']}: {rep['nota']} ({rep['hora']})",
            icon=folium.Icon(color="red", icon="warning", prefix="fa")
        ).add_to(capa_alertas)

    folium.LayerControl().add_to(m)
    st_folium(m, width="100%", height=450)

    # ---------------------------------------------------------
    # 5. LEYES, DERECHOS Y FICOSEC
    # ---------------------------------------------------------
    st.divider()
    st.markdown("### ⚖️ Marco Jurídico y Derechos")
    col_ley, col_der = st.columns(2)

    with col_ley:
        with st.expander("📜 Ley de Acceso a una Vida Libre de Violencia"):
            st.write("Establece que los establecimientos aliados deben garantizar resguardo inmediato a cualquier mujer en riesgo.")
    with col_der:
        with st.expander("🛡️ Tus Derechos en GeoGuard"):
            st.write("- Derecho a ser resguardada sin ser juzgada.")
            st.write("- Acceso a llamada de emergencia gratuita.")

    st.divider()
    st.markdown("### 🏛️ Instituciones Aliadas")
    c_f1, c_f2 = st.columns([1, 4])
    with c_f1:
        st.title("🏢")
    with c_f2:
        st.markdown("**FICOSEC (Chihuahua)**")
        st.write("Observatorio ciudadano que ofrece apoyo legal y psicológico gratuito (*2232).")
        st.link_button("Ir al sitio de FICOSEC", "https://ficosec.org/")

    # ---------------------------------------------------------
    # 6. CHAT CON IA (GEMINI)
    # ---------------------------------------------------------
    st.divider()
    st.subheader("🤖 GeoGuard AI: Asistente Virtual")
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if p := st.chat_input("Pregunta sobre refugios o leyes..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"):
            st.markdown(p)
        with st.chat_message("assistant"):
            model, instruct = inicializar_ia('puntos_chihuahua.csv', MI_API_KEY)
            r = obtener_respuesta_ia(p, model, instruct)
            st.markdown(r)
            st.session_state.messages.append({"role": "assistant", "content": r})

else:
    st.error("Archivo 'puntos_chihuahua.csv' no encontrado.")