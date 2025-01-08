# utils.py

import json
import logging
import hashlib
import random

def generate_preshared_key():
    """Genera una clave precompartida aleatoria."""
    key = hashlib.sha256(str(random.random()).encode()).hexdigest()
    return key

def delete_x1a(data):
    """Elimina caracteres no deseados (por ejemplo, '\\x1a') del mensaje."""
    return data.replace('\x1a', '')

def client_auth(connection):
    """Simula la autenticación del cliente."""
    try:
        # Aquí puedes agregar un proceso de autenticación real si es necesario.
        connection.send(b'AUTH_SUCCESS\x1a')
        return True
    except Exception as e:
        logging.error(f"Error en la autenticación: {e}")
        return False

def read_config(filename):
    """Lee el archivo de configuración JSON."""
    try:
        with open(filename, 'r') as file:
            config = json.load(file)
            return config
    except FileNotFoundError:
        logging.error(f"Archivo de configuración {filename} no encontrado.")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Error al leer el archivo JSON: {e}")
        raise

def find_event_type(event, config):
    """
    Busca el tipo de evento en el mapeo definido en config.json.
    Devuelve los detalles del evento o None si no se encuentra.
    """
    event_id = event.split(",")[1]  # Asume que el segundo elemento es el ID del evento
    event_mapping = config.get("mapping_events", {})
    return event_mapping.get(event_id)
