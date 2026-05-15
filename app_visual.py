import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from math import radians, cos, sin, asin, sqrt
from datetime import datetime
from ia_helper import inicializar_ia, obtener_respuesta_ia

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="GeoGuard - Chihuahua", layout="wide", page_icon="🛡️")

# --- CONEXIÓN CON LA API (USANDO SECRETS) ---
try:
    MI_API_KEY = st.secrets["AIzaSyB5KosUMhYmE6TMmPSBYTAAH1oXHDFqXpQ"]
except:
    MI_API_KEY = "AIzaSyB5KosUMhYmE6TMmPSBYTAAH1oXHDFqXpQ"

# FUNCIONES MATEMÁTICAS
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371
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

# ESTADOS DE SESIÓN
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'reportes' not in st.session_state:
    st.session_state.reportes = []

df = cargar_datos()

# --- SIDEBAR: ALERTAS CIUDADANAS (PUNTO 2 REFINADO) ---
st.sidebar.title("🕹️ Panel de Control")

if not df.empty:
    st.sidebar.subheader("📢 Reporte Comunitario")
    with st.sidebar.form("form_alerta", clear_on_submit=True):
        tipo = st.selectbox("Tipo de riesgo:", ["Persona sospechosa", "Acoso", "Calle sin luz", "Otro"])
        nota = st.text_area("Detalles:")
        enviar = st.form_submit_button("Publicar Alerta")
        
        if enviar and nota:
            st.session_state.reportes.append({
                "tipo": tipo, "nota": nota, 
                "lat": 28.633, "lon": -106.069, # Ubicación base
                "hora": datetime.now().strftime("%H:%M")
            })
            st.sidebar.success("✅ Alerta compartida con la red GeoGuard.")

    st.sidebar.divider()
    municipio = st.sidebar.selectbox("Filtrar Ciudad:", ["Todos"] + sorted(df['municipio'].unique()))

# --- CUERPO PRINCIPAL: MAPA ---
st.title("🛡️ GeoGuard: Red de Seguridad Chihuahua")

m = folium.Map(location=[28.633, -106.069], zoom_start=7, tiles="cartodbpositron")
cluster = MarkerCluster(name="Refugios").add_to(m)
alertas_layer = folium.FeatureGroup(name="Alertas Rojas").add_to(m)

# Dibujar Refugios del CSV
df_view = df if municipio == "Todos" else df[df['municipio'] == municipio]
for _, r in df_view.iterrows():
    folium.Marker(
        [r['Latitud'], r['Longitud']], 
        popup=f"<b>{r['Nombre']}</b><br>{r['Telefono']}",
        icon=folium.Icon(color="orange", icon="shield", prefix="fa")
    ).add_to(cluster)

# Dibujar Alertas del usuario
for rep in st.session_state.reportes:
    folium.Marker(
        [rep['lat'], rep['lon']], 
        popup=f"⚠️ {rep['tipo']}: {rep['nota']}",
        icon=folium.Icon(color="red", icon="warning", prefix="fa")
    ).add_to(alertas_layer)

st_folium(m, width="100%", height=400)

# --- SECCIÓN DE LEYES Y FICOSEC ---
col1, col2 = st.columns(2)
with col1:
    with st.expander("⚖️ Marco Jurídico"):
        st.write("Ley de Acceso a una Vida Libre de Violencia del Estado de Chihuahua.")
with col2:
    with st.expander("🏛️ Instituciones Aliadas"):
        st.write("**FICOSEC:** Apoyo legal gratuito marcando al *2232.")

# --- CHAT CON IA ---
st.divider()
st.subheader("🤖 Consulta a GeoGuard AI")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if p := st.chat_input("¿En qué puedo ayudarte?"):
    st.session_state.messages.append({"role": "user", "content": p})
    with st.chat_message("user"): st.markdown(p)
    
    with st.chat_message("assistant"):
        model, instruct = inicializar_ia('puntos_chihuahua.csv', MI_API_KEY)
        r = obtener_respuesta_ia(p, model, instruct)
        st.markdown(r)
        st.session_state.messages.append({"role": "assistant", "content": r})