import os
from dotenv import load_dotenv

load_dotenv()

class S3Config:
    def __init__(self):
        self.S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY_ID")
        self.S3_ACCESS_KEY_SECRET = os.getenv("S3_ACCESS_KEY_SECRET")
        self.S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

    def config_dict(self):
        return {
            "access_key": self.S3_ACCESS_KEY,
            "access_key_secret": self.S3_ACCESS_KEY_SECRET,
            "bucket_name": self.S3_BUCKET_NAME
        }
    
class KafkaConfig:
    def __init__(self):
        self.KAFKA_SERVER_IP = os.getenv("KAFKA_SERVER_IP")
        self.KAFKA_SERVER_PORT = os.getenv("KAFKA_SERVER_PORT")
        self.KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")

    def config_dict(self):
        return {
            "server_ip": self.KAFKA_SERVER_IP,
            "server_port": self.KAFKA_SERVER_PORT,
            "topic": self.KAFKA_TOPIC
        }
    
# class APIConfig:
#     def __init__(self):
#         self.base_url = os.getenv("ALPHA_VANTAGE_BASE_URL")
#         self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

#     def config_dict(self):
#         return {
#             "base_url": self.base_url,
#             "api_key": self.api_key
#         }