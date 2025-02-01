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
import queue
from logs.logs_parser import parse_log

import pandas as pd

import streamlit as st

setup_logging()

producer_queue = queue.Queue()
consumer_queue = queue.Queue()

last_fetched_time = None

def producer_task():
    global last_fetched_time
    logger = logging.getLogger("producer")
    # Get configs
    kafka_config = KafkaConfig().config_dict()

    producer = setup_producer(kafka_config, serializer.serialize)
    producer.flush()

    while True:
        # Get data from API
        symbols = ["AAPL", "GOOGL", "MSFT"]
        filtered = filter_stock_data(symbols)
        if filtered is not None:
            data, last_fetched_time = filtered
            logger.debug(f"last_fetched_time = {last_fetched_time}")
        else:
            data = filtered
        
        if data is not None and not data.empty:
            for _, record in data.iterrows():
                record_dict = record.to_dict()
                producer.send(kafka_config["topic"], value=record_dict)
                logger.debug(f"Produced record => {record_dict['Timestamp']} {record_dict['Symbol']}:: Open: {record_dict['Open']}, Low: {record_dict['Low']}, High: {record_dict['High']}, Close: {record_dict['Close']}, Volume: {record_dict['Volume']}")
                producer_queue.put(record.to_dict())
        else:
            logger.debug(f"No new data to produce")

        time.sleep(5) # Change to 1 hour pulls


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
            consumer_queue.put(data)

if __name__ == "__main__":
    logger = logging.getLogger("main")
    # Run producer and consumer as separate threads
    producer_thread = threading.Thread(target=producer_task, daemon=True)
    consumer_thread = threading.Thread(target=consumer_task, daemon=True)
    
    # Start the threads
    producer_thread.start()
    consumer_thread.start()
    
    logger.debug("Producer and Consumer are running.")
    
    # Also serve UI from this
    st.title("📈 Real-time Stock Data Healthcheck")
    last_fetched_time_placeholder = st.empty()

    producer_data_list = []
    consumer_data_list = []

    row1_cols = st.columns(2)
    producer_health_placeholder = row1_cols[0].empty()
    producer_placeholder = row1_cols[0].empty()
    consumer_health_placeholder = row1_cols[1].empty()
    consumer_placeholder = row1_cols[1].empty()

    row2_cols = st.columns(2)
    row2_cols[0].subheader("Pull Log Last")
    pull_log = row2_cols[0].empty()
    row2_cols[0].subheader("Producer Log Last")
    producer_log = row2_cols[0].empty()
    row2_cols[1].subheader("Push Log Last")
    push_log = row2_cols[1].empty()
    row2_cols[1].subheader("Consumer Log Last")
    consumer_log = row2_cols[1].empty()


    # Keep the main thread alive
    try:
        while True:
            if last_fetched_time is not None:
                last_fetched_time_placeholder.subheader(f"Data last fetched at {last_fetched_time}")

            while not producer_queue.empty():
                producer_data_list.append(producer_queue.get())

            while not consumer_queue.empty():
                consumer_data_list.append(consumer_queue.get())

            if producer_data_list:
                producer_health_placeholder.subheader(f"Producer running healthy")
                producer_df = pd.DataFrame(producer_data_list)
                producer_placeholder.dataframe(producer_df)
            else:
                producer_health_placeholder.subheader(f"Producer may have issues")
                producer_placeholder.text("Waiting for new data")
            
            if consumer_data_list:
                consumer_health_placeholder.subheader(f"Consumer running healthy")
                consumer_df = pd.DataFrame(consumer_data_list)
                consumer_placeholder.dataframe(consumer_df)
            else:
                consumer_health_placeholder.subheader(f"Consumer may have issues")
                consumer_placeholder.text("Waiting for new data")

            with open("logs/pull.log", "r") as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1]
                    parsed_last_line = parse_log(last_line)
                    pull_log.write(f"{parsed_last_line['timestamp']}: {parsed_last_line['message']}")

            with open("logs/push.log", "r") as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1]
                    parsed_last_line = parse_log(last_line)
                    push_log.write(f"{parsed_last_line['timestamp']}: {parsed_last_line['message']}")
                
            with open("logs/consumer.log", "r") as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1]
                    parsed_last_line = parse_log(last_line)
                    consumer_log.write(f"{parsed_last_line['timestamp']}: {parsed_last_line['message']}")

            with open("logs/producer.log", "r") as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1]
                    parsed_last_line = parse_log(last_line)
                    producer_log.write(f"{parsed_last_line['timestamp']}: {parsed_last_line['message']}")

            time.sleep(1) # Update UI every second
    except KeyboardInterrupt:
        logger.debug("Shutting down...")
    except Exception as e:
        logger.error(e)