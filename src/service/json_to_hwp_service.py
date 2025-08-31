# json_to_hwp_service.py

from src.util.hwp_convert_util import make_hwp_controller
from datetime import datetime
import os
from src.service import s3_service
from kafka import KafkaProducer


class JsonToHwpService:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:19092','localhost:19093','localhost:19094'],
            value_serializer=lambda v: v.encode('utf-8')
        )
        self.s3 = s3_service.S3Service()

    def convert_json_to_hwp(self, event):
        # 이벤트 수신
        if isinstance(event, str):
            import json
            event = json.loads(event)
            print("Parsed event:", event)

        file_id = event['id']
        file_key = event['fileName']

        # S3에서 json 파일 다운로드
        json_contents = self.s3.get_file_contents(file_key)

        # HWP 변환 로직 시작
        hwp_path = make_hwp_controller(json_contents)

        # S3 업로드 - 완성된 hwp 파일
        upload_file_name = os.path.basename(hwp_path)
        date_prefix = datetime.now().strftime('%Y/%m')
        upload_key = f'jsonToHwpComplete/{date_prefix}/{upload_file_name}'
        self.s3.upload_file(hwp_path, upload_key)

        # 완료 이벤트 발행(id, 완성된 hwp 파일 s3 주소)
        completed_event = {
            'id': file_id,
            'fileName': upload_key,
        }
        self.producer.send('jsonToHwpComplete', value=completed_event)
        self.producer.flush()  # 즉시 전송 보장

