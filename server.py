# coding: utf-8

from socket import socket, AF_INET, SOCK_STREAM, timeout, SOL_SOCKET, SO_REUSEADDR
import logging
import sys
import traceback
import time
import threading
import os
from utils import generate_preshared_key, delete_x1a, client_auth, read_config, find_event_type
from mqtt import mqtt_start_server, mqtt_ha_config

# Configuración de logging
def setup_logging():
    log = logging.getLogger()
    out_hdlr = logging.StreamHandler()
    out_hdlr.setFormatter(logging.Formatter('[%(asctime)s] - %(module)s - %(levelname)s - %(message)s'))
    log.addHandler(out_hdlr)
    try:
        log.setLevel(os.environ["LOGLEVEL"])
        out_hdlr.setLevel(os.environ["LOGLEVEL"])
    except KeyError:
        print("Please set the environment variable LOGLEVEL")
        sys.exit(1)
    return log

log = setup_logging()

def main():
    try:
        cfg = read_config("config.json")
        start_alarm_server(cfg)
    except KeyError:
        log.error("Missing configuration file: config.json")
        sys.exit(1)

def start_alarm_server(cfg):
    host, port = cfg["socket_bind"], cfg["socket_listen_port"]

    try:
        soc = create_socket(host, port)
        mqtt_client = setup_mqtt(cfg)
        accept_connections(soc, mqtt_client, cfg)
    except Exception as e:
        log.error(f"Fatal error: {e}")
        sys.exit(1)

def create_socket(host, port):
    soc = socket(AF_INET, SOCK_STREAM)
    soc.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    log.info("Socket created")
    try:
        soc.bind((host, port))
        soc.listen(5)
        log.info("Socket now listening")
    except Exception as e:
        log.error(f"Socket error: {e}")
        sys.exit(1)
    return soc

def setup_mqtt(cfg):
    try:
        mqtt_client = mqtt_start_server(cfg)
        if cfg["home_assistant_integration"]:
            mqtt_ha_config(mqtt_client, cfg)
        return mqtt_client
    except Exception as e:
        log.error(f"MQTT setup failed: {e}")
        raise

def accept_connections(soc, mqtt_client, cfg):
    while True:
        connection, address = soc.accept()
        log.info(f"### Connected with {address[0]}:{address[1]} ###")
        threading.Thread(target=client_thread, args=(connection, address, mqtt_client, cfg)).start()

def client_thread(connection, address, mqtt_client, cfg, max_buffer_size=5120):
    ip, port = address
    log.info(f"Thread started for {ip}:{port}")
    connection.settimeout(cfg["socket_timeout"])
    try:
        if not handle_auth(connection):
            connection.close()
            return

        while True:
            data = connection.recv(max_buffer_size)
            if data:
                handle_received_data(data, mqtt_client, cfg)
            else:
                break
    except timeout:
        log.warning(f"Connection timeout for {ip}:{port}")
    except Exception as e:
        log.error(f"Error in client thread: {e}")
    finally:
        connection.close()
        log.info(f"Connection closed for {ip}:{port}")

def handle_auth(connection):
    if client_auth(connection):
        log.info("Client authenticated")
        return True
    else:
        log.warning("Client authentication failed")
        return False

def handle_received_data(data, mqtt_client, cfg):
    try:
        if b"EVENT" in data:
            handle_event(data.decode(), mqtt_client, cfg)
        elif b"FILE" in data:
            log.info("Received FILE, sending ACK")
            connection.send(b'FILE_ACK\x1a')
        elif b"REQACK" in data:
            log.info("Received REQACK, sending simple ACK")
            connection.send(b'ACK\x1a')
    except Exception as e:
        log.error(f"Error handling data: {e}")

def handle_event(event, mqtt_client, cfg):
    log.info(f"Processing EVENT: {delete_x1a(event)}")
    event_data = find_event_type(delete_x1a(event), cfg)
    if not event_data:
        return
    try:
        topic = f"{cfg['mqtt_prefix']}/{cfg['home_assistant_sensors'][event_data['type']]['sensor_type']}/{event_data['type']}/state"
        mqtt_client.publish(topic, event_data["state"], 0)
        log.info(f"MQTT updated: {event_data}")
    except Exception as e:
        log.error(f"Error publishing MQTT data: {e}")

if __name__ == "__main__":
    main()
