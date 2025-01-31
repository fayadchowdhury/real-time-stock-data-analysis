from typing import Callable
from kafka import KafkaProducer
import logging

def setup_producer(server_params: dict, value_serializer: Callable[[any], bytes]) -> KafkaProducer:
    try:
        logger = logging.getLogger("producer")
        server_ip = server_params["server_ip"]
        server_port = server_params["server_port"]
        logger.debug(f"Trying to connect producer to {server_ip}:{server_port}")
        producer = KafkaProducer(
            bootstrap_servers=f"{server_ip}:{server_port}",
            value_serializer=lambda x: value_serializer(x)
        )
        logger.debug(f"Producer for {server_ip}:{server_port} setup successful")
        return producer
    except Exception as e:
        logger.error(e)
        return None