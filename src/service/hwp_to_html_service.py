# hwp_to_html.py

from src.util.hwp_convert_util import convert_formular_to_text
from datetime import datetime
import os
import uuid
from src.service import s3_service
from kafka import KafkaProducer
import shutil
import src.util.common_util as common_util
import json


class HwpToHtmlService:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:19092', 'localhost:19093', 'localhost:19094'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.s3 = s3_service.S3Service()

    def convert_hwp_to_html(self, event):
        # 이벤트 수신
        if isinstance(event, str):
            event = json.loads(event)

        file_id = event['id']
        file_key = event['fileName']

        # 파일 다운로드
        extension = file_key.rsplit('.', 1)[-1]
        file_name = f"{uuid.uuid4()}.{extension}"
        resource_path = os.path.join(common_util.get_resource_path(), "convertHwp")

        os.makedirs(resource_path, exist_ok=True)
        file_full_path = os.path.join(resource_path, file_name)

        self.s3.download_file(file_key, file_full_path)
        # HWP → HTML ZIP 변환
        html_zip_file = convert_formular_to_text(file_name) + ".zip"

        # S3 업로드
        upload_file_name = os.path.basename(html_zip_file)
        date_prefix = datetime.now().strftime('%Y/%m')
        upload_key = f'hwpToHtmlComplete/{date_prefix}/{upload_file_name}'
        self.s3.upload_file(html_zip_file, upload_key)

        # 완료 이벤트 발행
        completed_event = {
            'id': file_id,
            'fileName': upload_key,
        }
        self.producer.send('hwpToHtmlComplete', value=completed_event)
        self.producer.flush()
