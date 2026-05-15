from google import genai
import pandas as pd

def inicializar_ia(csv_path, api_key):
    """Configura el cliente de IA con el contexto de Chihuahua."""
    # Inicializamos el cliente con la nueva librería google-genai
    client = genai.Client(api_key=api_key)
    
    try:
        df = pd.read_csv(csv_path)
        df.columns = df.columns.str.strip()
        contexto_refugios = df.to_string(index=False)
    except:
        contexto_refugios = "Información de refugios en Chihuahua disponible localmente."

    instrucciones = f"""
    Eres 'GeoGuard AI', asistente experta en seguridad para mujeres en Chihuahua.
    Datos de refugios: {contexto_refugios}
    
    REGLAS DE ORO:
    1. Si hay riesgo, indica el Punto Naranja o refugio más cercano con su dirección.
    2. Menciona a FICOSEC (*2232) para asesoría legal y psicológica gratuita.
    3. Si la ciudad no está en la lista, recomienda llamar al 911 de inmediato.
    4. Usa un tono protector, profesional y empático.
    """
    return client, instrucciones

def obtener_respuesta_ia(mensaje_usuario, client, instrucciones):
    """Genera respuesta usando el modelo gemini-1.5-flash."""
    try:
        # Llamada al modelo con el nuevo formato
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=f"{instrucciones}\n\nPregunta de la usuaria: {mensaje_usuario}"
        )
        return response.text
    except Exception as e:
        # Este mensaje saldrá si no hay internet o la llave falló
        return "⚠️ Tuve un problema de conexión con Google. Revisa tu Wi-Fi o intenta de nuevo."