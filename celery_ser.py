from clientsService import celery_app
from botocore.exceptions import NoCredentialsError, BotoCoreError
from clientsService import ses_client
import fitz  # PyMuPDF for PDF processing
from docx import Document
from OpenAIPower import model
from jsonschema import validate, ValidationError
from Sample_Data import json_schema, Prompt_modifier


@celery_app.task
def sendMail(EmailFormat,sesClient=ses_client):
        try:
            response = sesClient.send_email(**EmailFormat)
            print("Email sent! Message ID:", response["MessageId"])
            return True
        except (NoCredentialsError, BotoCoreError) as e:
            print("Error sending email:", str(e))
            return False   

