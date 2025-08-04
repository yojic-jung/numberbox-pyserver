# main.py

from apscheduler.schedulers.background import BackgroundScheduler
from src.kafka import kafka_client
from kafka import KafkaConsumer
from src.scheduler import job_scheduler
from src.service.json_to_hwp_service import JsonToHwpService
from src.service.hwp_to_html_service import HwpToHtmlService
import os
from kafka.errors import KafkaError
import botocore.exceptions
import threading

# 루트 경로 지정
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.environ["PROJECT_ROOT"] = PROJECT_ROOT

# 스케줄러 등록
scheduler = BackgroundScheduler(timezone='Asia/Seoul')
scheduler.start()
scheduler.add_job(job_scheduler.delete_old_file_folder, 'cron', hour='04', minute='00', id="job_1")

# Kafka Producer는 공유 인스턴스
producer = kafka_client.create_producer()

# 서비스 클래스 인스턴스 생성
json_service = JsonToHwpService()
html_service = HwpToHtmlService()


def process_message(message, consumer):
    try:
        if message.topic == 'jsonToHwp':
            json_service.convert_json_to_hwp(message.value)
        elif message.topic == 'hwpToHtml':
            html_service.convert_hwp_to_html(message.value)
        else:
            print(f"Unknown topic: {message.topic}")

        # 처리 성공 시 비동기 커밋
        consumer.commit_async()

    except (KafkaError, botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        # 재시도 대상 예외
        retry_count = int(dict(message.headers).get('retry_count', b'0').decode())
        if retry_count == 0:
            next_topic = 'retry_topic_1'
        elif retry_count == 1:
            next_topic = 'retry_topic_2'
        else:
            next_topic = 'dlq_topic'

        headers = [('retry_count', str(retry_count + 1).encode())]

        producer.send(next_topic, key=message.key, value=message.value, headers=headers)
        producer.flush()
        consumer.commit_sync()

        print(f"[RETRY] 메시지 재전송 → {next_topic}, 오류: {e}")

    except Exception as e:
        # 기타 예외 → 바로 DLQ
        producer.send('dlq_topic', key=message.key, value=message.value, headers=[('reason', str(e).encode())])
        producer.flush()
        consumer.commit_sync()

        print(f"[DLQ] 재처리 불가 예외, 메시지 DLQ 전송: {e}")


def start_consumer_thread():
    consumer = KafkaConsumer(
        'jsonToHwp',
        'hwpToHtml',
        bootstrap_servers=['localhost:9092'],
        group_id='numberbox-convert-group',
        enable_auto_commit=False,
        auto_offset_reset='earliest',
        value_deserializer=lambda m: m.decode('utf-8')
    )
    for message in consumer:
        process_message(message, consumer)


# 3개의 쓰레드로 Kafka consumer 실행
for _ in range(3):
    print("Kafka Consumer Thread 시작")
    t = threading.Thread(target=start_consumer_thread)
    t.start()
