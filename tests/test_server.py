# coding: utf-8

import socket
import time
import logging

# Configuración del logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
log = logging.getLogger()

# Configuración del servidor de prueba
SERVER_HOST = "127.0.0.1"  # Cambiar si el servidor está en otra IP
SERVER_PORT = 888          # Asegurarse de que coincida con el servidor

# Función para enviar eventos al servidor
def send_event(event_message, delay=1):
    """
    Envía un mensaje de evento al servidor y espera la respuesta.
    Args:
        event_message (str): Mensaje del evento a enviar.
        delay (int): Tiempo de espera entre envíos.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            log.info(f"Conectando a {SERVER_HOST}:{SERVER_PORT}")
            client_socket.connect((SERVER_HOST, SERVER_PORT))

            log.info(f"Enviando evento: {event_message}")
            client_socket.sendall(event_message.encode())

            # Leer respuesta del servidor (si aplica)
            response = client_socket.recv(1024).decode()
            log.info(f"Respuesta del servidor: {response}")

            time.sleep(delay)
    except Exception as e:
        log.error(f"Error al enviar el evento: {e}")

# Función principal para simular diferentes eventos
def main():
    log.info("Iniciando script de pruebas...")

    # Eventos de prueba (personalizarlos según el sistema RSI)
    events = [
        "EVENT,1,2,1",  # Intrusión detectada
        "EVENT,3,62,0",  # Autoprotección iniciada
        "EVENT,4",  # Fin de autoprotección
        "EVENT,19",  # Pérdida de energía eléctrica
        "EVENT,20",  # Recuperación de energía
        "EVENT,24,1,3",  # Sistema armado
        "EVENT,25,0,3",  # Sistema desarmado
    ]

    for event in events:
        send_event(event, delay=2)

    log.info("Pruebas finalizadas.")

if __name__ == "__main__":
    main()
