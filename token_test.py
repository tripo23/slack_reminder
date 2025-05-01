import requests
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener el token de Slack desde el archivo .env
slack_token = os.getenv("SLACK_TOKEN")

# URL para probar la autenticación con el token
url = "https://slack.com/api/auth.test"

# Encabezados para la solicitud, con el token de Slack
headers = {
    "Authorization": f"Bearer {slack_token}"
}

def verificar_token():
    print("entro a la funcion de verificar")
    try:
        # Hacer la solicitud GET a la API de Slack
        response = requests.get(url, headers=headers)
        
        # Si la respuesta es exitosa
        if response.status_code == 200:
            data = response.json()  # Parsear la respuesta JSON
            if data['ok']:
                print(f"Token válido. Usuario: {data['user']} y equipo: {data['team']}")
            else:
                print(f"Error en la autenticación: {data['error']}")
        else:
            print(f"Error al conectar con Slack. Código de estado: {response.status_code}")
    except Exception as e:
        print(f"Error al hacer la solicitud: {e}")

if __name__ == "__main__":
    verificar_token()