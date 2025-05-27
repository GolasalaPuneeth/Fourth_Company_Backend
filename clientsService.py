import boto3
import os
from botocore.exceptions import NoCredentialsError, BotoCoreError
from celery import Celery
from dotenv import dotenv_values

config = dotenv_values(".env")

ses_client = boto3.client("ses", region_name=config["region_name"],
aws_access_key_id=config["aws_access_key_id"],
aws_secret_access_key=config["aws_secret_access_key"]
)



celery_app = Celery(
    "tasks",
    broker=config['broker'], 
    backend=config['Que_backend'],
    result_expires=300
)