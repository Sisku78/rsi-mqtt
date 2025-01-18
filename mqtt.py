import paho.mqtt.client as mqtt
import logging
import json

def mqtt_start_server(config):
    """
    Inicializa la conexión MQTT y maneja reconexiones.
    """
    try:
        client = mqtt.Client()

        # Establecer credenciales
        client.username_pw_set(config["mqtt_user"], config["mqtt_password"])

        # Configurar callbacks opcionales
        client.on_connect = lambda client, userdata, flags, rc: logging.info("Conexión MQTT exitosa")
        client.on_disconnect = lambda client, userdata, rc: logging.warning("Conexión MQTT perdida")

        # Conectar al broker MQTT
        client.connect(config["mqtt_host"], config["mqtt_port"], keepalive=60)
        logging.info(
            f"Conexión MQTT establecida con {config['mqtt_host']}:{config['mqtt_port']} "
            f"usando usuario '{config['mqtt_user']}'"
        )

        # Iniciar el loop MQTT
        client.loop_start()
        return client
    except Exception as e:
        logging.error(f"Error al conectar con el servidor MQTT: {e}")
        raise

def mqtt_ha_config(client, config):
    """
    Publica configuraciones para sensores en Home Assistant con validaciones.
    """
    try:
        sensors = config.get("home_assistant_sensors", {})
        for sensor, details in sensors.items():
            # Validar que las claves requeridas existan
            if not all(k in details for k in ("device_class",)):
                logging.warning(f"Configuración incompleta para el sensor: {sensor}")
                continue

            # Construir el tema y el payload
            topic = f"{config['mqtt_prefix']}/binary_sensor/{sensor}/config"
            payload = {
                "name": sensor,
                "device_class": details["device_class"],
                "state_topic": f"{config['mqtt_prefix']}/binary_sensor/{sensor}/state",
                "unique_id": sensor,
                "payload_on": "ON",
                "payload_off": "OFF",
                "availability_topic": f"{config['mqtt_prefix']}/status",
                "payload_available": "online",
                "payload_not_available": "offline",
            }

            # Publicar la configuración en el broker MQTT
            client.publish(topic, json.dumps(payload), retain=True)
            logging.info(f"Configuración publicada para el sensor: {sensor}")

    except Exception as e:
        logging.error(f"Error al configurar Home Assistant: {e}")
        raise
