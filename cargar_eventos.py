import firebase_admin
from firebase_admin import credentials, firestore
import json

# Cargar las credenciales y conectar con Firebase
cred = credentials.Certificate("service_account_firebase.json")  # Asegúrate de que este archivo esté en la ruta correcta
firebase_admin.initialize_app(cred)

# Obtener referencia a Firestore
db = firestore.client()

# Leer eventos desde el archivo eventos.json
def cargar_eventos():
    print("Comienza carga de eventos")
    try:
        with open('eventos.json', 'r') as archivo:
            eventos = json.load(archivo)

        # Insertar cada evento en Firestore
        eventos_ref = db.collection(u'eventos')  # Usamos la colección 'eventos'
        
        for evento in eventos:
            # Insertar cada evento como un documento
            eventos_ref.add(evento)

        print(f"{len(eventos)} eventos cargados correctamente en Firestore.")
    
    except Exception as e:
        print(f"Error al cargar los eventos en Firestore: {e}")

# Llamar la función para cargar los eventos
cargar_eventos()