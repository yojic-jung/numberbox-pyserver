# json_to_hwp_service.py

from src.util.hwp_convert_util import make_hwp_controller
from datetime import datetime
import os
from src.service import s3_service
import src.kafka.kafka_client as kafka_client


class JsonToHwpService:
    def __init__(self):
        self.producer = kafka_client.create_producer()
        self.s3 = s3_service.S3Service()

    def convert_json_to_hwp(self, event):
        try:
            # 이벤트 수신
            file_id = event['id']
            file_key = event['fileName']
            print(f" 수신된 메시지: id={file_id}, key={file_key}")

            # S3에서 json 파일 다운로드
            json_contents = self.s3.get_file_contents(file_key)
            print(f" S3에서 파일 다운로드 완료: {file_key}")

            # HWP 변환 로직 시작

            hwp_path = make_hwp_controller(json_contents)
            print(f" HWP 생성 완료: {hwp_path}")

            # S3 업로드 - 완성된 hwp 파일
            upload_file_name = os.path.basename(hwp_path)
            print(upload_file_name)
            date_prefix = datetime.now().strftime('%Y/%m')
            upload_key = f'jsonToHwpComplete/{date_prefix}/{upload_file_name}'
            print(upload_key)
            self.s3.upload_file(hwp_path, upload_key)

            # 완료 이벤트 발행(id, 완성된 hwp 파일 s3 주소)
            completed_event = {
                'id': file_id,
                'fileName': upload_key,
            }
            self.producer.send('jsonToHwpComplete', value=completed_event)
            self.producer.flush()  # 즉시 전송 보장
            print(f" HWP 생성 완료 이벤트 발행")

        except Exception as e:
            print(f" 처리 중 오류 발생: {e}")
