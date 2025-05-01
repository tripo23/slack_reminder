import requests
import os
import json
import threading
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener el token de Slack desde el archivo .env
slack_token = os.getenv("SLACK_TOKEN")

# El canal al que se enviará el mensaje
channel = "#producto-leads"  # Cambia esto al canal que desees

# URL de la API de Slack para enviar mensajes
url = "https://slack.com/api/chat.postMessage"

# Encabezados, incluyendo el token de autorización
headers = {
    "Authorization": f"Bearer {slack_token}",
    "Content-Type": "application/json"
}

# Hora fija para el recordatorio (por ejemplo, 16:28)
hora_recordatorio = "09:15"

def leer_eventos():
    """Leer los eventos desde el archivo JSON"""
    try:
        with open('eventos.json', 'r') as archivo:
            eventos = json.load(archivo)
        return eventos
    except Exception as e:
        print(f"Error al leer el archivo de eventos: {e}")
        return []

def enviar_mensaje(evento):
    """Envía un mensaje de recordatorio a Slack"""
    # Si la hora es "TBD", enviamos el mensaje pero indicando que la hora aún no está definida
    if evento['hora'] == "TBD":
        hora_mensaje = "aún no definida"
    else:
        hora_mensaje = evento['hora']
    
    data = {
        "channel": channel,
        "text": f"¡Holaaaa! Paso a avisar que, en el próximo sprint, se viene '{evento['nombre']}'! Va a ser el {evento['fecha']} a las {hora_mensaje}. ¡Dejemos todo listo para brillar!"
    }
    
    try:
        # Enviar la solicitud POST a Slack
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            print(f"Mensaje enviado para: {evento['nombre']}")
        else:
            print(f"Error al enviar el mensaje: {response.text}")
    except Exception as e:
        print(f"Error al hacer la solicitud: {e}")

def programar_recordatorio(evento):
    """Programa el recordatorio 20 días antes del evento, siempre a una hora fija"""
    # Comprobamos si la hora es "TBD", pero aún así enviamos el mensaje
    fecha_evento = datetime.strptime(f"{evento['fecha']} {evento['hora']}", "%d/%m/%Y %H:%M") if evento['hora'] != "TBD" else datetime.strptime(f"{evento['fecha']} 00:00", "%d/%m/%Y %H:%M")
    
    fecha_recordatorio = fecha_evento - timedelta(days=20)
    
    # Cambiar la hora del recordatorio a la hora fija (16:28)
    hora_fija = datetime.strptime(hora_recordatorio, "%H:%M").time()
    fecha_recordatorio = datetime.combine(fecha_recordatorio, hora_fija)
    
    # Calculamos el tiempo de espera (en segundos) hasta la fecha del recordatorio
    tiempo_espera = (fecha_recordatorio - datetime.now()).total_seconds()
    
    # Verificamos si ya pasó el tiempo para enviar el recordatorio
    if tiempo_espera > 0:
        print(f"Recordatorio para '{evento['nombre']}' programado para el {fecha_recordatorio}")
        
        # Esperamos hasta la fecha programada
        time.sleep(tiempo_espera)
        enviar_mensaje(evento)
    else:
        print(f"El evento '{evento['nombre']}' ya pasó o está muy cerca de la fecha para programar el recordatorio.")

def programar_eventos():
    """Crea un hilo por cada evento para ejecutar los recordatorios de forma independiente"""
    eventos = leer_eventos()  # Leer los eventos desde el archivo JSON
    if eventos:
        for evento in eventos:
            # Crear un nuevo hilo para cada recordatorio
            hilo = threading.Thread(target=programar_recordatorio, args=(evento,))
            hilo.start()

if __name__ == "__main__":
    programar_eventos()