# Setting Up Kafka on EC2

## 1. Set Up the EC2 Instance
1. Set up an EC2 instance on the free tier.
2. Log in using EC2 Connect.

## 2. Install Prerequisites
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

## 3. Configure Kafka
1. Edit the `config/server.properties` file to update the `advertised.listeners` hostname to the EC2 public IP. *(Consider if this should be an Elastic IP for persistence.)*

## 4. Start Zookeeper
### Option 1: Start Manually
Run:
```bash
<path-to-kafka-directory>/bin/zookeeper-server-start.sh config/zookeeper.properties
```

### Option 2: Run as a Service
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

## 5. Start Kafka
### Option 1: Start Manually
1. Set the Kafka heap size:
   ```bash
   export KAFKA_HEAP_OPTS="-Xmx256M -Xms128M"
   ```
2. Start Kafka:
   ```bash
   <path-to-kafka-directory>/bin/kafka-server-start.sh config/server.properties
   ```

### Option 2: Run as a Service
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

# Using Kafka

## 1. Create a Topic
Run:
```bash
<path-to-kafka-directory>/bin/kafka-topics.sh --create --topic topic --bootstrap-server ec2-public-ip:9092 --replication-factor 1 --partitions 1
```

## 2. Create a Producer
Run:
```bash
<path-to-kafka-directory>/bin/kafka-console-producer.sh --topic topic --bootstrap-server ec2-public-ip:9092
```
*(Consider creating a service for a producer that sends random data sampled from a dataset.)*

## 3. Create a Consumer
Run:
```bash
<path-to-kafka-directory>/bin/kafka-console-consumer.sh --topic topic --bootstrap-server ec2-public-ip:9092
```

---

# Python Setup for Kafka Consumer and Producer

## 1. Install Dependencies
Install `kafka-python-ng` (compatible with Python 3.11+):
```bash
pip install kafka-python-ng
```
Put AWS IAM User access key ID, access key secret and S3 bucket name in .env file in project root

## 2. Create a Producer
- Develop a producer based on `experiments/kafka-producer.ipynb`.
- The producer will sample a random row from the dataset every 5 seconds and push it to the Kafka topic stream.

## 3. Create a Consumer
- Develop a consumer based on `experiments/kafka-consumer.ipynb`.
- The consumer will read data from the Kafka stream and push it to an S3 bucket (one file per record).

---

# AWS Glue Integration

## 1. Set Up Glue Crawler
1. Assign an IAM role to AWS Glue to access the S3 bucket.
2. Create a database in Glue to store the crawled metadata.
3. Set up a crawler to scan the S3 bucket and write metadata to the database.

## 2. Query Data with Athena
- Use AWS Athena to run SQL queries on the S3 data.
- Specify an output location for query results in Athena settings.

---

# Next Steps
1. Convert the code into a monolithic application with an interface to connect to a stock API.
2. Integrate with AWS QuickSight for dashboards and reporting.
3. Explore Infrastructure-as-Code tools like Boto3 or Pulumi.
4. Investigate using Confluent for managing the Kafka server.