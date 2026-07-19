import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_notificacion(empleos_nuevos: list):
    if not empleos_nuevos:
        print("[Telegram] No hay empleos nuevos para notificar.")
        return

    print(f"[Telegram] Preparando {len(empleos_nuevos)} notificaciones...")
    
    url_api = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    # Definimos cuántos empleos queremos enviar por cada mensaje de Telegram
    tamano_lote = 5
    
    # Recorremos la lista de empleos en saltos de 5 en 5
    for i in range(0, len(empleos_nuevos), tamano_lote):
        lote = empleos_nuevos[i:i + tamano_lote]
        
        # Construimos un solo bloque de texto para todo el lote
        texto_mensaje = "<b>Nuevas vacantes encontradas:</b>\n\n"
        for empleo in lote:
            texto_mensaje += f"Puesto: <b>{empleo['puesto']}</b>\n"
            texto_mensaje += f"Empresa: {empleo['empresa']}\n"
            texto_mensaje += f"Portal: {empleo['portal']}\n"
            texto_mensaje += f"<a href='{empleo['url']}'>Aplicar aquí</a>\n"
            texto_mensaje += "-----------------------\n"
            
        payload = {
            "chat_id": CHAT_ID,
            "text": texto_mensaje,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        
        try:
            respuesta = requests.post(url_api, data=payload)
            respuesta.raise_for_status()
        except Exception as e:
            print(f"[Telegram] Error enviando mensaje: {e}")
            
    print("[Telegram] Todas las notificaciones enviadas con éxito en bloques.")