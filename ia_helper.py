import google.generativeai as genai
import pandas as pd

def inicializar_ia(csv_path, api_key):
    """Configura el modelo y carga el contexto del CSV."""
    genai.configure(api_key=api_key)
    
    try:
        df = pd.read_csv(csv_path)
        contexto_refugios = df.to_string(index=False)
    except Exception as e:
        contexto_refugios = "No se pudieron cargar los datos de refugios."

    # Usamos un nombre de modelo estándar que funciona en todas las regiones
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    instrucciones = f"""
    Eres 'GeoGuard AI', asistente experta en seguridad ciudadana en Chihuahua.
    Tu objetivo es ayudar a mujeres en riesgo usando estos datos de refugios:
    {contexto_refugios}
    
    REGLAS:
    1. Si la usuaria está en peligro, indica el Punto Naranja más cercano con dirección y teléfono.
    2. Menciona a FICOSEC (*2232) para asesoría legal y psicológica gratuita.
    3. Si la ciudad no está en el mapa, recomienda llamar al 911.
    4. Sé empática, directa y profesional.
    """
    return model, instrucciones

def obtener_respuesta_ia(mensaje_usuario, model, instrucciones):
    """Genera la respuesta asegurando que no se rompa la sesión."""
    try:
        prompt = f"{instrucciones}\n\nPregunta de la usuaria: {mensaje_usuario}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "Lo siento, tuve un problema de conexión. Por favor, intenta de nuevo o llama al 911."