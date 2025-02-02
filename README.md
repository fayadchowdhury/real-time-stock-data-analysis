# Real-Time Stock Data Monitoring App

This project is a monolithic application that fetches stock data using the `yfinance` API, processes it in real-time with Kafka, and provides a Streamlit-based UI for monitoring system health. The app runs as a service with the producer and consumer running on individual threads.

## Installation and Running the App

1. Clone the repository:
   ```bash
   git clone https://github.com/fayadchowdhury/real-time-stock-data-analysis.git
   cd real-time-stock-data-analysis
   ```

2. Install dependencies:
   ```bash
   poetry install --no-root
   ```

3. Run the Streamlit dashboard:
   ```bash
   poetry run streamlit run main.py
   ```

The Streamlit UI provides health checks including:
- Last lines of the pull, push, consumer, and producer logs
- Timestamp of the last fetched data
- Last few records of fetched data

---

## Setting Up Kafka on EC2

### 1. Set Up the EC2 Instance
1. Set up an EC2 instance on the free tier.
2. Log in using EC2 Connect.

### 2. Install Prerequisites
1. Install Amazon Corretto 11:
   ```bash
   sudo yum install java-11-amazon-corretto-headless
   ```
2. Download Apache Kafka:
   ```bash
   wget https://downloads.apache.org/kafka/3.7.2/kafka_2.12-3.7.2.tgz
   ```
3. Extract the Kafka archive:
   ```bash
   tar -xvf kafka_2.12-3.7.2.tgz
   ```

### 3. Configure Kafka
Edit the `config/server.properties` file to update the `advertised.listeners` hostname to the EC2 public IP. *(Consider using an Elastic IP for persistence.)*

### 4. Start Zookeeper
#### Option 1: Start Manually
```bash
<path-to-kafka-directory>/bin/zookeeper-server-start.sh config/zookeeper.properties
```

#### Option 2: Run as a Service
1. Create a Zookeeper service file:
   ```bash
   sudo nano /etc/systemd/system/zookeeper.service
   ```
2. Add the following content:
   ```ini
   [Unit]
   Requires=network.target remote-fs.target
   After=network.target remote-fs.target

   [Service]
   Type=simple
   User=ec2-user
   ExecStart=/home/ec2-user/kafka_2.12-3.7.2/bin/zookeeper-server-start.sh /home/ec2-user/kafka_2.12-3.7.2/config/zookeeper.properties
   ExecStop=/home/ec2-user/kafka_2.12-3.7.2/bin/zookeeper-server-stop.sh
   Restart=on-abnormal

   [Install]
   WantedBy=multi-user.target
   ```
3. Start the service:
   ```bash
   sudo systemctl start zookeeper.service
   ```
4. Enable the service to start on boot:
   ```bash
   sudo systemctl enable zookeeper.service
   ```

### 5. Start Kafka
#### Option 1: Start Manually
1. Set the Kafka heap size:
   ```bash
   export KAFKA_HEAP_OPTS="-Xmx256M -Xms128M"
   ```
2. Start Kafka:
   ```bash
   <path-to-kafka-directory>/bin/kafka-server-start.sh config/server.properties
   ```

#### Option 2: Run as a Service
1. Create a Kafka service file:
   ```bash
   sudo nano /etc/systemd/system/kafka.service
   ```
2. Add the following content:
   ```ini
   [Unit]
   Requires=zookeeper.service
   After=zookeeper.service

   [Service]
   Type=simple
   User=ec2-user
   Environment="KAFKA_HEAP_OPTS=-Xmx256M -Xms128M"
   ExecStart=/home/ec2-user/kafka_2.12-3.7.2/bin/kafka-server-start.sh /home/ec2-user/kafka_2.12-3.7.2/config/server.properties
   ExecStop=/home/ec2-user/kafka_2.12-3.7.2/bin/kafka-server-stop.sh
   Restart=on-abnormal

   [Install]
   WantedBy=multi-user.target
   ```
3. Start the service:
   ```bash
   sudo systemctl start kafka.service
   ```
4. Enable the service to start on boot:
   ```bash
   sudo systemctl enable kafka.service
   ```

---

## Using Kafka

### 1. Create a Topic
```bash
<path-to-kafka-directory>/bin/kafka-topics.sh --create --topic topic --bootstrap-server ec2-public-ip:9092 --replication-factor 1 --partitions 1
```

### 2. Create a Producer
```bash
<path-to-kafka-directory>/bin/kafka-console-producer.sh --topic topic --bootstrap-server ec2-public-ip:9092
```

### 3. Create a Consumer
```bash
<path-to-kafka-directory>/bin/kafka-console-consumer.sh --topic topic --bootstrap-server ec2-public-ip:9092
```

---

## AWS Glue Integration

### 1. Set Up Glue Crawler
1. Assign an IAM role to AWS Glue to access the S3 bucket.
2. Create a database in Glue to store the crawled metadata.
3. Set up a crawler to scan the S3 bucket based on metadata schema.
4. Optionally set up ETL jobs such as getting rid of NULL values and saving as parquet files partitioned on ticker symbol etc.

### 2. Query Data with Athena
- Use AWS Athena to run SQL queries on the S3 data.
- Specify an output location for query results in Athena settings.

---

## Next Steps
1. The app now connects to the `yfinance` API instead of AlphaVantage.
2. Looking into PowerBI for visualization instead of QuickSight.
3. Confluent wasn't necessary but may be revisited later.
4. Exploring Infrastructure-as-Code (Boto3, Pulumi) in the future.
