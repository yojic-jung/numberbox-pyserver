# hwp_to_html.py

from src.util.hwp_convert_util import convert_formular_to_text
from datetime import datetime
import os
import uuid
from src.service import s3_service
from kafka import KafkaProducer
import shutil
import src.util.common_util as common_util


class HwpToHtmlService:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:19092','localhost:19093','localhost:19094'],
            value_serializer=lambda v: v.encode('utf-8')
        )
        self.s3 = s3_service.S3Service()

    def convert_hwp_to_html(self, event):
        try:
            # 이벤트 수신
            if isinstance(event, str):
                import json
                event = json.loads(event)
                print("Parsed event:", event)
            file_id = event['id']
            file_key = event['fileName']
            print(f" 수신된 메시지: id={file_id}, key={file_key}")

            # 파일 다운로드
            extension = file_key.rsplit('.', 1)[-1]
            fileName = f"{uuid.uuid4()}.{extension}"
            fileFullName = common_util.get_resource_path() + "\\convertHwp\\" + fileName
            self.s3.download_file(file_key, fileFullName)

            # hwp to html zip 변환
            htmlZipFileName = convert_formular_to_text(fileName) + ".zip"
            print(htmlZipFileName)

            # S3 업로드 - 완성된 html zip 파일
            upload_file_name = os.path.basename(htmlZipFileName)
            date_prefix = datetime.now().strftime('%Y/%m')
            upload_key = f'hwpToHtmlComplete/{date_prefix}/{upload_file_name}'
            self.s3.upload_file(htmlZipFileName, upload_key)

            # 완료 이벤트 발행(id, 완성된 hwp 파일 s3 주소)
            completed_event = {
                'id': file_id,
                'fileName': upload_key,
            }
            self.producer.send('hwpToHtmlComplete', value=completed_event)
            self.producer.flush()  # 즉시 전송 보장
            print(f" HTML 생성 완료 이벤트 발행")

            # zip파일 삭제
            os.remove(htmlZipFileName)
            # 폴더 삭제
            shutil.rmtree(htmlZipFileName, onerror=common_util.remove_readonly)
        except Exception as e:
            print(f" 처리 중 오류 발생: {e}")
