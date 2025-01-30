from config.config import S3Config, KafkaConfig
from network.pull import filter_stock_data
from network.push import push_to_cloud
from producer.producer import setup_producer
from consumer.consumer import setup_consumer
from converters import serializer, deserializer
import time
import threading
import logging
from config.logging import setup_logging

setup_logging()

def producer_task():
    logger = logging.getLogger("producer")
    # Get configs
    kafka_config = KafkaConfig().config_dict()

    producer = setup_producer(kafka_config, serializer.serialize)
    producer.flush()

    while True:
        # Get data from API
        symbols = ["AAPL", "GOOGL", "MSFT"]
        data = filter_stock_data(symbols)
        
        if data is not None and not data.empty:
            for _, record in data.iterrows():
                producer.send(kafka_config["topic"], value=record.to_dict())
                logger.debug(f"Produced record: {record}")
        else:
            logger.debug(f"No new data to produce")

        time.sleep(3600) # Change to 1 hour pulls


def consumer_task():
    logger = logging.getLogger("consumer")
    # Get configs
    s3_config = S3Config().config_dict()
    kafka_config = KafkaConfig().config_dict()

    consumer = setup_consumer(kafka_config, deserializer.deserialize)
    consumer.subscribe([kafka_config["topic"]])

    while True:
        for message in consumer:
            data = message.value
            logger.debug(f"Consumed record: {data}")
            push_to_cloud(s3_config, data["Symbol"], data["Timestamp"], data)
            

if __name__ == "__main__":
    logger = logging.getLogger("main")
    # Run producer and consumer as separate threads
    producer_thread = threading.Thread(target=producer_task, daemon=True)
    consumer_thread = threading.Thread(target=consumer_task, daemon=True)
    
    # Start the threads
    producer_thread.start()
    consumer_thread.start()
    
    logger.debug("Producer and Consumer are running.")
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.debug("Shutting down...")