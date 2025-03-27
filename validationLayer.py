from pydantic import BaseModel,EmailStr,HttpUrl

class MailResponse(BaseModel):
    mail_status: bool
    
class EmailContent(BaseModel):
    SENDER :EmailStr = "info@hashtechinfo.com"
    RECIPIENT :EmailStr = "info@hashtechinfo.com"
    SUBJECT: str
    BODY_TEXT: str
    BODY_HTML: str

class Base_asserts(BaseModel):
    id: int
    full_name: str
    designation: str
    comment: str
    image_url: str

class Domains_url(BaseModel):
    class Config:
        json_encoders = {
            HttpUrl: str 
        }
    ID: int
    Service_name: str
    URL: HttpUrl
    logoImage: HttpUrl
    smallDescription: str

class UserInfo(BaseModel):
    FULLNAME:str
    PHONE: int
    EMAIL_client: EmailStr
    MESSAGE: str
    SOURCE: str