import os
import boto3
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError

# Load environment variables from .env file
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME')
AWS_REGION = os.getenv('AWS_REGION') or 'ap-southeast-1'

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)


class S3Handler():

    def __init__(self):
        pass

    def upload_file_data_to_s3(self, file_data, file_name=None, bucket_name=AWS_S3_BUCKET_NAME):
        """Upload a file to an S3 bucket

        :param file_data: File data to upload
        :param file_name: S3 object name. If not specified then file_name is used
        :param bucket_name: Bucket to upload to
        :return: True if file was uploaded, else False
        """
        try:
            s3_client.upload_fileobj(file_data, bucket_name, file_name)
            return f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_name}"
        except NoCredentialsError:
            print("---[x] Credentials not available")
            return False

    def upload_file_to_s3(self, local_file_path, s3_file_name=None, bucket_name=AWS_S3_BUCKET_NAME, extra_args=None):
        try:
            s3_client.upload_file(local_file_path, bucket_name, s3_file_name, ExtraArgs=extra_args)
            return f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_file_name}"
        except NoCredentialsError:
            print("---[x] Credentials not available")
            return False


s3_handler_instance = S3Handler()
