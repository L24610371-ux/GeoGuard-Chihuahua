import google.generativeai as genai
import pandas as pd

def inicializar_ia(csv_path, api_key):
    genai.configure(api_key=api_key)
    
    try:
        df = pd.read_csv(csv_path)
        contexto_refugios = df.to_string(index=False)
    except:
        contexto_refugios = "No hay datos de refugios disponibles."
    
    # --- DIAGNÓSTICO DINÁMICO ---
    modelos_disponibles = []
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                modelos_disponibles.append(m.name)
        
        # Intentamos usar el primero de la lista que sea Gemini
        # Esto evita el error 404 porque usamos lo que la API nos diga que tiene
        if modelos_disponibles:
            # Buscamos alguno que sea gemini-1.5 o gemini-pro
            seleccionado = next((x for x in modelos_disponibles if "gemini-1.5" in x), modelos_disponibles[0])
            model = genai.GenerativeModel(seleccionado)
        else:
            raise Exception("No se encontraron modelos compatibles.")
            
    except Exception as e:
        # Si todo falla, intentamos el nombre genérico más básico
        model = genai.GenerativeModel('gemini-pro')

    instrucciones = f"""
    Eres 'GeoGuard AI', asistente de seguridad en Chihuahua. 
    Usa estos datos de refugios para ayudar:
    {contexto_refugios}
    Reglas: Si hay peligro, da el teléfono del refugio más cercano.
    """
    return model, instrucciones

def obtener_respuesta_ia(mensaje_usuario, model, instrucciones):
    try:
        # Usamos la forma más simple posible de enviar el mensaje
        response = model.generate_content(f"{instrucciones}\n\nUsuaria: {mensaje_usuario}")
        return response.text
    except Exception as e:
        return f"Lo siento, sigo teniendo problemas de conexión: {str(e)}"