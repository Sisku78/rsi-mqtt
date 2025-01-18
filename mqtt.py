import paho.mqtt.client as mqtt
import logging
import json

def mqtt_start_server(config):
    """
    Inicializa la conexión MQTT.
    Devuelve el cliente MQTT.
    """
    try:
        client = mqtt.Client()

        # Establecer credenciales del usuario MQTT
        client.username_pw_set(config["mqtt_user"], config["mqtt_password"])

        # Conectar al broker MQTT con un keep-alive de 60 segundos
        client.connect(config["mqtt_host"], config["mqtt_port"], keepalive=60)
        logging.info(
            f"Conexión MQTT establecida con {config['mqtt_host']}:{config['mqtt_port']} "
            f"usando usuario '{config['mqtt_user']}'"
        )

        # Inicia el loop MQTT en un hilo separado
        client.loop_start()
        return client
    except Exception as e:
        logging.error(f"Error al conectar con el servidor MQTT: {e}")
        raise

def mqtt_ha_config(client, config):
    """
    Publica configuraciones para sensores en Home Assistant.
    """
    try:
        sensors = config.get("home_assistant_sensors", {})
        for sensor, details in sensors.items():
            # Construir el tema MQTT de configuración
            topic = f"{config['mqtt_prefix']}/binary_sensor/{sensor}/config"
            
            # Crear el payload JSON para el sensor
            payload = {
                "name": sensor,
                "device_class": details["device_class"],
                "state_topic": f"{config['mqtt_prefix']}/binary_sensor/{sensor}/state",
                "unique_id": sensor,
                "payload_on": "ON",
                "payload_off": "OFF",
                "availability_topic": f"{config['mqtt_prefix']}/status",
                "payload_available": "online",
                "payload_not_available": "offline"
            }
            
            # Publicar la configuración en el tema
            client.publish(topic, json.dumps(payload), retain=True)
            logging.info(f"Configuración publicada para el sensor: {sensor}")

    except Exception as e:
        logging.error(f"Error al configurar Home Assistant: {e}")
        raise

