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
        try:
            self.s3.upload_file(local_file_path, self.bucket_name, s3_key)
            print(f" 다운로드 성공: {local_file_path}")
        except ClientError as e:
            print(f" 업로드 실패: {e}")

    def download_file(self, s3_key, local_file_path):
        try:
            self.s3.download_file(self.bucket_name, s3_key, local_file_path)
            print(f"다운로드 성공: {local_file_path}")
        except ClientError as e:
            print(f"다운로드 실패: {e}")

    def get_file_contents(self, s3_key):
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=s3_key)
            data = response['Body'].read()  # 바이트 데이터 읽기
            text = data.decode('utf-8')  # utf-8 텍스트로 변환
            return text
        except Exception as e:
            print(f"S3에서 객체를 읽는 중 오류 발생: {e}")
