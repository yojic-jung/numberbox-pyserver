# main.py

from apscheduler.schedulers.background import BackgroundScheduler
from src.kafka import kafka_client
from src.scheduler import job_scheduler
from src.service.json_to_hwp_service import JsonToHwpService
from src.service.hwp_to_html_service import HwpToHtmlService
import os

# 루트 경로 지정
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.environ["PROJECT_ROOT"] = PROJECT_ROOT

# 스케줄러 등록
scheduler = BackgroundScheduler(timezone='Asia/Seoul')
scheduler.start()
scheduler.add_job(job_scheduler.delete_old_file_folder, 'cron', hour='04', minute='00', id="job_1")

# Kafka Consumer 초기화
consumer = kafka_client.create_consumer()

# 서비스 클래스 인스턴스 생성
json_service = JsonToHwpService()
html_service = HwpToHtmlService()

# 메시지 처리 루프
for message in consumer:
    try:
        topic = message.topic
        if topic == 'jsonToHwp':
            json_service.convert_json_to_hwp(message.value)
        elif topic == 'hwpToHtml':
            html_service.convert_hwp_to_html(message.value)
        else:
            print(f"Unknown topic: {topic}")
    except Exception as e:
        print(f" 처리 중 오류 발생: {e}")
