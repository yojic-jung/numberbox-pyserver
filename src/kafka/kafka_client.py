from kafka import KafkaConsumer, KafkaProducer
import json
import os
from src.util import common_util
from dotenv import load_dotenv

# .env 파일 불러오기
load_dotenv()

# Kafka 설정
KAFKA_BROKER = os.getenv("KAFKA_BROKER")
KAFKA_TOPICS = os.getenv("KAFKA_CONVERT_TOPICS", "")
GROUP_ID = os.getenv("KAFKA_GROUP_ID")


def create_consumer():
    topics = [t.strip() for t in KAFKA_TOPICS.split(",") if t.strip()]
    consumer = KafkaConsumer(
        bootstrap_servers=[KAFKA_BROKER],
        group_id=GROUP_ID,
        value_deserializer=common_util.safe_json_deserializer,
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )
    consumer.subscribe(topics)
    return consumer


def create_producer():
    return KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
