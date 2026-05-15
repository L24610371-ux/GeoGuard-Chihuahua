import google.generativeai as genai
import pandas as pd

def inicializar_ia(csv_path, api_key):
    """Configura el modelo y carga el contexto del CSV de Chihuahua."""
    genai.configure(api_key=api_key)
    
    try:
        df = pd.read_csv(csv_path)
        # Limpiar espacios en los nombres de las columnas
        df.columns = df.columns.str.strip()
        contexto_refugios = df.to_string(index=False)
    except Exception as e:
        contexto_refugios = "No se pudieron cargar los datos de refugios localmente."

    # Usamos gemini-1.5-flash por su velocidad y estabilidad
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    instrucciones = f"""
    Eres 'GeoGuard AI', asistente experta en seguridad para mujeres en el estado de Chihuahua.
    Tu objetivo es brindar información clara y empática basada en estos datos:
    {contexto_refugios}
    
    REGLAS DE RESPUESTA:
    1. Si detectas una emergencia, prioriza el Punto Naranja o refugio más cercano.
    2. Menciona siempre a FICOSEC (*2232) para asesoría legal gratuita.
    3. Si la usuaria menciona una ciudad que no está en la lista, recomiéndale llamar al 911.
    4. Usa un tono profesional, protector y directo.
    """
    return model, instrucciones

def obtener_respuesta_ia(mensaje_usuario, model, instrucciones):
    """Genera la respuesta y maneja errores de conexión."""
    try:
        prompt = f"{instrucciones}\n\nPregunta de la usuaria: {mensaje_usuario}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "⚠️ Error de conexión con la IA. Por favor, verifica tu internet o llama directamente al 911."