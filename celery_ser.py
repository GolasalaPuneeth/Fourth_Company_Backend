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

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])


def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text 
        
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

def convert_text_to_json(text: str) -> dict:
    ai_msg = model.invoke(Prompt_modifier(text))
    try:
        validate(instance=ai_msg, schema=json_schema)
        print("✅ AI response is valid and follows the schema.")
        return ai_msg
    except ValidationError as e:
        print("❌ AI response is INVALID!")
        print("Error:", e.message)
        return f"Error: {e.message}"
        


@celery_app.task
def extract_and_convert_to_json(file_path, file_type):
    if file_type == "docx":
        raw_text = extract_text_from_docx(file_path)
    elif file_type == "pdf":
        raw_text = extract_text_from_pdf(file_path)
    else:
        raise ValueError("Unsupported format")
    
    json_result = convert_text_to_json(raw_text)
    return json_result