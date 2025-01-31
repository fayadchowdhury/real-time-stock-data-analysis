from typing import Callable
from kafka import KafkaConsumer
import logging

def setup_consumer(server_params: dict, value_deserializer: Callable[[bytes], any]) -> KafkaConsumer:
    logger = logging.getLogger("consumer")
    try:
        server_ip = server_params["server_ip"]
        server_port = server_params["server_port"]
        logger.debug(f"Trying to connect consumer to {server_ip}:{server_port}")
        consumer = KafkaConsumer(
            bootstrap_servers=f"{server_ip}:{server_port}",
            value_deserializer=lambda x: value_deserializer(x)
        )
        logger.info(f"Consumer at {server_ip}:{server_port} setup successful")
        return consumer
    except Exception as e:
        logger.error(e)
        return None