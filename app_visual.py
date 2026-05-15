import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from datetime import datetime
from ia_helper import inicializar_ia, obtener_respuesta_ia

# CONFIGURACIÓN INICIAL
st.set_page_config(page_title="GeoGuard - Chihuahua", layout="wide", page_icon="🛡️")

# --- MANEJO ROBUSTO DE LA API KEY ---
try:
    # Intenta leer de los Secrets (Nube)
    MI_API_KEY = st.secrets["AIzaSyB5KosUMhYmE6TMmPSBYTAAH1oXHDFqXpQ"]
except:
    # Si falla, usa la llave directa (Laptop local)
    # REEMPLAZA ESTO CON TU LLAVE REAL PARA PROBAR EN TU PC
    MI_API_KEY = "AIzaSyB5KosUMhYmE6TMmPSBYTAAH1oXHDFqXpQ" 

# CARGA DE DATOS
@st.cache_data
def cargar_datos():
    try:
        data = pd.read_csv('puntos_chihuahua.csv')
        data.columns = data.columns.str.strip()
        return data
    except:
        st.error("No se encontró el archivo puntos_chihuahua.csv")
        return pd.DataFrame()

# SESIÓN PARA CHAT Y REPORTES
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'reportes' not in st.session_state:
    st.session_state.reportes = []

df = cargar_datos()

# --- PANEL LATERAL (ALERTA CIUDADANA) ---
st.sidebar.title("🕹️ Panel de Control")
if not df.empty:
    st.sidebar.subheader("📢 Reportar Incidente")
    with st.sidebar.form("form_alerta", clear_on_submit=True):
        tipo = st.selectbox("Tipo:", ["Persona sospechosa", "Acoso", "Calle sin luz"])
        nota = st.text_area("Descripción:")
        enviar = st.form_submit_button("Publicar en Mapa")
        
        if enviar and nota:
            st.session_state.reportes.append({
                "tipo": tipo, "nota": nota, 
                "lat": 28.633, "lon": -106.069, # Coordenadas base de Chihuahua
                "hora": datetime.now().strftime("%H:%M")
            })
            st.sidebar.success("Alerta enviada a la red.")

# --- CUERPO PRINCIPAL ---
st.title("🛡️ GeoGuard: Red de Seguridad Chihuahua")

# Crear Mapa
m = folium.Map(location=[28.633, -106.069], zoom_start=7, tiles="cartodbpositron")
cluster = MarkerCluster(name="Refugios").add_to(m)

# Dibujar Refugios del CSV
for _, r in df.iterrows():
    folium.Marker(
        [r['Latitud'], r['Longitud']], 
        popup=f"<b>{r['Nombre']}</b><br>Tel: {r['Telefono']}",
        icon=folium.Icon(color="orange", icon="shield", prefix="fa")
    ).add_to(cluster)

# Dibujar Alertas en tiempo real
for rep in st.session_state.reportes:
    folium.Marker(
        [rep['lat'], rep['lon']], 
        popup=f"⚠️ {rep['tipo']}: {rep['nota']}",
        icon=folium.Icon(color="red", icon="warning", prefix="fa")
    ).add_to(m)

st_folium(m, width="100%", height=450)

# INFORMACIÓN EXTRA
col1, col2 = st.columns(2)
with col1:
    with st.expander("⚖️ Marco Jurídico"):
        st.info("Ley de Acceso a una Vida Libre de Violencia (Chihuahua).")
with col2:
    with st.expander("🏛️ Apoyo FICOSEC"):
        st.info("Marca al *2232 para apoyo legal y psicológico gratuito 24/7.")

# --- SECCIÓN DE CHAT IA ---
st.divider()
st.subheader("🤖 Consultar a GeoGuard AI")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("¿Cómo puedo ayudarte hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        # Verificamos que la llave no esté vacía antes de llamar a la IA
        if MI_API_KEY and MI_API_KEY != "TU_LLAVE_AQUI":
            model, instruct = inicializar_ia('puntos_chihuahua.csv', MI_API_KEY)
            respuesta = obtener_respuesta_ia(prompt, model, instruct)
            st.markdown(respuesta)
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
        else:
            st.warning("Configura tu API Key para activar la IA.")