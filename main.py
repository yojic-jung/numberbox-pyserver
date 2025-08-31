# main.py

from apscheduler.schedulers.background import BackgroundScheduler
from kafka import KafkaConsumer
from kafka import KafkaProducer
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
producer = KafkaProducer(
        bootstrap_servers=['localhost:19092','localhost:19093','localhost:19094'],
        value_serializer=lambda v: v.encode('utf-8')
    )

# 서비스 클래스 인스턴스 생성
json_service = JsonToHwpService()
html_service = HwpToHtmlService()

def process_message(message, consumer):
    try:
        if message.topic == 'numberbox.convert.jsonToHwp.request':
            print("토픽 메시지 처리")
            json_service.convert_json_to_hwp(message.value)
        elif message.topic == 'numberbox.convert.hwpToHtml.request':
            html_service.convert_hwp_to_html(message.value)
        else:
            print(f"Unknown topic: {message.topic}")
        # 처리 성공 시 비동기 커밋
        consumer.commit_async()

    except (KafkaError, botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        # 재시도 대상 예외
        print("retry")

        retry_topic = 'numberbox.convert.hwpToHtml.retry.request'

        producer.send(retry_topic, key=message.key, value=message.value)
        producer.flush()
        consumer.commit()

    except Exception as e:
        print("dlq")
        # 기타 예외 → 바로 DLQ
        producer.send('numberbox.convert.hwpToHtml.dlq.request', key=message.key, value=message.value, headers=[('reason', str(e).encode())])
        producer.flush()
        consumer.commit()


def start_consumer_thread():
    consumer = KafkaConsumer(
        'numberbox.convert.jsonToHwp.request',
        'numberbox.convert.hwpToHtml.request',
        bootstrap_servers=['localhost:19092','localhost:19093','localhost:19094'],
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

# 메인 스레드 대기
while True:
    import time
    time.sleep(60)