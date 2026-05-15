import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from datetime import datetime
from ia_helper import inicializar_ia, obtener_respuesta_ia

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="GeoGuard - Chihuahua", layout="wide", page_icon="🛡️")

# --- MANEJO DE API KEY (Nube y Local) ---
try:
    # Intenta leer de los secretos de Streamlit Cloud (Nube)
    MI_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    # SI ESTÁS EN TU LAPTOP, CAMBIA ESTO POR TU LLAVE REAL
    MI_API_KEY = "AIzaSyBGOwmjXOohR61LlLbX-ZACsNKDsmz7Jxc" 

@st.cache_data
def cargar_datos():
    try:
        data = pd.read_csv('puntos_chihuahua.csv')
        data.columns = data.columns.str.strip()
        return data
    except:
        return pd.DataFrame()

# ESTADOS DE SESIÓN (Chat y Alertas)
if 'messages' not in st.session_state: st.session_state.messages = []
if 'reportes' not in st.session_state: st.session_state.reportes = []

df = cargar_datos()

# --- PANEL LATERAL (REPORTES) ---
st.sidebar.title("🕹️ Panel de Control")
if not df.empty:
    st.sidebar.subheader("📢 Reporte Comunitario")
    with st.sidebar.form("form_alerta", clear_on_submit=True):
        tipo = st.selectbox("Tipo de riesgo:", ["Persona sospechosa", "Acoso", "Calle sin luz"])
        nota = st.text_area("Detalles:")
        enviar = st.form_submit_button("Publicar Alerta")
        if enviar and nota:
            st.session_state.reportes.append({
                "tipo": tipo, "nota": nota, "lat": 28.633, "lon": -106.069,
                "hora": datetime.now().strftime("%H:%M")
            })
            st.sidebar.success("✅ Alerta compartida en la red.")

# --- CUERPO PRINCIPAL ---
st.title("🛡️ GeoGuard: Red de Seguridad Chihuahua")

# Mapa Interactivo
m = folium.Map(location=[28.633, -106.069], zoom_start=7, tiles="cartodbpositron")
cluster = MarkerCluster(name="Refugios").add_to(m)

# Dibujar Puntos Naranja del CSV
if not df.empty:
    for _, r in df.iterrows():
        folium.Marker(
            [r['Latitud'], r['Longitud']], 
            popup=f"<b>{r['Nombre']}</b><br>Tel: {r['Telefono']}",
            icon=folium.Icon(color="orange", icon="shield", prefix="fa")
        ).add_to(cluster)

# Dibujar Alertas del usuario en tiempo real
for rep in st.session_state.reportes:
    folium.Marker(
        [rep['lat'], rep['lon']], 
        popup=f"⚠️ {rep['tipo']}: {rep['nota']}",
        icon=folium.Icon(color="red", icon="warning", prefix="fa")
    ).add_to(m)

st_folium(m, width="100%", height=400)

# --- SECCIÓN DE LEYES Y FICOSEC ---
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader("⚖️ Marco Jurídico")
    with st.expander("Ver fundamentos legales"):
        st.write("""
        **Ley de Acceso de las Mujeres a una Vida Libre de Violencia (Chihuahua):**
        Este proyecto se fundamenta en el **Artículo 9**, que promueve la creación de mecanismos 
        digitales y físicos para la protección inmediata y canalización a refugios.
        """)

with col2:
    st.subheader("🏛️ Instituciones Aliadas")
    with st.expander("Información de FICOSEC"):
        st.info("**FICOSEC (Línea Ciudadana):**")
        st.write("""
        Marca al ** *2232 ** o al **800 999 2232**.
        Brindan acompañamiento legal y psicológico gratuito las 24 horas del día.
        """)

# --- CHAT CON IA (VERSIÓN FINAL) ---
st.divider()
st.subheader("🤖 Consulta a GeoGuard AI")

# Historial de chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# Entrada de la usuaria
if prompt_user := st.chat_input("¿En qué puedo ayudarte hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt_user})
    with st.chat_message("user"): st.markdown(prompt_user)
    
    with st.chat_message("assistant"):
        # Verificamos que haya una llave puesta
        if MI_API_KEY and len(MI_API_KEY) > 10:
            try:
                client, instruct = inicializar_ia('puntos_chihuahua.csv', MI_API_KEY)
                respuesta = obtener_respuesta_ia(prompt_user, client, instruct)
                st.markdown(respuesta)
                st.session_state.messages.append({"role": "assistant", "content": respuesta})
            except Exception as e:
                st.error("No se pudo conectar con el servicio de IA.")
        else:
            st.warning("⚠️ Configura tu API Key en el código para activar la IA.")