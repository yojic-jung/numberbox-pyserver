# s3_service.py

import boto3
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# .env 파일 불러오기
load_dotenv()


class S3Service:
    def __init__(self):
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )

    def upload_file(self, local_file_path, s3_key):
        self.s3.upload_file(local_file_path, self.bucket_name, s3_key)

    def download_file(self, s3_key, local_file_path):
        self.s3.download_file(self.bucket_name, s3_key, local_file_path)


    def get_file_contents(self, s3_key):
        response = self.s3.get_object(Bucket=self.bucket_name, Key=s3_key)
        data = response['Body'].read()  # 바이트 데이터 읽기
        text = data.decode('utf-8')  # utf-8 텍스트로 변환
        return text
