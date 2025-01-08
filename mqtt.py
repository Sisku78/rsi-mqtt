# mqtt.py

import paho.mqtt.client as mqtt
import logging

def mqtt_start_server(config):
    """
    Inicializa la conexión MQTT.
    Devuelve el cliente MQTT.
    """
    try:
        client = mqtt.Client()
        client.connect(config["mqtt_host"], config["mqtt_port"])
        logging.info("Conexión MQTT establecida.")
        return client
    except Exception as e:
        logging.error(f"Error al conectar con el servidor MQTT: {e}")
        raise

def mqtt_ha_config(client, config):
    """
    Publica configuraciones para Home Assistant basadas en el archivo config.json.
    """
    try:
        sensors = config.get("home_assistant_sensors", {})
        for sensor, details in sensors.items():
            topic = f"{config['mqtt_prefix']}/binary_sensor/{sensor}/config"
            payload = {
                "name": sensor,
                "device_class": details["device_class"],
                "state_topic": f"{config['mqtt_prefix']}/binary_sensor/{sensor}/state",
                "initial_state": details["default_state"]
            }
            client.publish(topic, json.dumps(payload), retain=True)
            logging.info(f"Configuración publicada para el sensor: {sensor}")
    except Exception as e:
        logging.error(f"Error al configurar Home Assistant: {e}")
        raise
