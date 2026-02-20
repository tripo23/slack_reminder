import firebase_admin
from firebase_admin import credentials, firestore
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
print("Token de Slack cargado.")

# El canal al que se enviará el mensaje
channel = "testtripo"  # Canal donde se va a enviar el mensaje. Asegúrate que el bot esté agregado previamente.

# URL de la API de Slack para enviar mensajes
url = "https://slack.com/api/chat.postMessage"

# Encabezados, incluyendo el token de autorización
headers = {
    "Authorization": f"Bearer {slack_token}",
    "Content-Type": "application/json"
}

# Hora fija para el recordatorio (por ejemplo, a las 12:15 UTC / 9:15 GMT-3)
hora_recordatorio = "12:15"
print("Hora de recordatorio establecida:", hora_recordatorio, "UTC")

# Cargar el archivo de credenciales desde el archivo JSON decodificado
cred = credentials.Certificate('service_account_firebase.json')  # Archivo decodificado
firebase_admin.initialize_app(cred)

# Obtener la referencia a la base de datos Firestore
db = firestore.client()

# Enviar un mensaje directo al canal
def enviar_mensaje_directo():

    print("Se ejecuta envio de mensaje directo")
    data = {
        "channel": channel,
        "text": "¡Holaaaa! Paso a avisar que hoy juega Boca vs Racing a las 20hs!"
    }
    
    try:
        # Enviar la solicitud POST a Slack
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            print("Mensaje directo enviado correctamente.")
        else:
            print(f"Error al enviar Mensaje directo: {response.text}")
    except Exception as e:
        print(f"Error al hacer la solicitud de Mensaje directo: {e}")


# Obtener los eventos de Firestore
def leer_eventos():
    """Leer los eventos desde Firestore"""
    try:
        eventos_ref = db.collection(u'eventos')  # Asumimos que los eventos están en la colección 'eventos'
        eventos = eventos_ref.stream()

        evento_lista = []
        for evento in eventos:
            evento_lista.append(evento.to_dict())  # Convertimos cada documento en un diccionario

        print(f"{len(evento_lista)} eventos leídos desde Firestore.")
        return evento_lista

    except Exception as e:
        print(f"Error al leer los eventos desde Firestore: {e}")
        return []

def enviar_mensaje(evento, cercano=False):
    """Envía un mensaje de recordatorio a Slack"""
    if evento['hora'] == "TBD":
        hora_mensaje = "aún no definida"
    else:
        hora_mensaje = evento['hora']

    if cercano:
        texto = f"⚠️ ¡En 3 días se viene {evento['nombre']}! Es este {evento['fecha']} a las {hora_mensaje}. ¡Últimos días para dejar todo listo!"
    else:
        texto = f"¡Holaaaa! Paso a avisar que, en el próximo sprint, se viene {evento['nombre']}! Va a ser el {evento['fecha']} a las {hora_mensaje}."

    data = {
        "channel": channel,
        "text": texto
    }
    
    try:
        # Enviar la solicitud POST a Slack
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            print(f"Mensaje enviado correctamente para: {evento['nombre']}")
        else:
            print(f"Error al enviar el mensaje para {evento['nombre']}: {response.text}")
    except Exception as e:
        print(f"Error al hacer la solicitud para {evento['nombre']}: {e}")


def programar_recordatorio(evento):
    print (f"Programando para {evento['nombre']}")
    fecha_evento = datetime.strptime(f"{evento['fecha']}", "%d/%m/%Y")
    print(f"Fecha del evento: {fecha_evento}")

    fecha_recordatorio = fecha_evento - timedelta(days=20)
    fecha_recordatorio_cercano = fecha_evento - timedelta(days=3)

    if (fecha_recordatorio.date() == datetime.now().date()):
        print(f"se va a enviar un recordatorio para {evento['nombre']}")
        enviar_mensaje(evento)

    if (fecha_recordatorio_cercano.date() == datetime.now().date()):
        print(f"se va a enviar un recordatorio para {evento['nombre']}")
        enviar_mensaje(evento, cercano=True)


def programar_eventos():
    eventos = leer_eventos()  # Leer los eventos desde Firestore
    if eventos:
        print(f"Se encontraron {len(eventos)} eventos para programar.")
        for evento in eventos:
            # Crear un nuevo hilo para cada recordatorio
            hilo = threading.Thread(target=programar_recordatorio, args=(evento,))
            hilo.start()
            print(f"Hilo iniciado para el evento: {evento['nombre']}")

if __name__ == "__main__":
    print("Iniciando la programación de eventos...")
    programar_eventos()
    enviar_mensaje_directo()