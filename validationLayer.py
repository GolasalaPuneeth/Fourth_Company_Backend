from pydantic import BaseModel,EmailStr,HttpUrl
from typing import Optional,List
from datetime import datetime,date
from sqlmodel import Field
from enum import Enum
from TMTdb_schemas import Job


class Status(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = 'CRITICAL'#Critical


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

class logger_info(BaseModel):
    Service : str
    Error_info : str

# ----------------------------------------------------------------

class SectionType(str, Enum):
    PERSONAL_INFO = "personal_info"
    PROFESSIONAL_SUMMARY = "professional_summary"
    SKILLS = "skills"
    WORK_EXPERIENCE = "work_experience"
    EDUCATION = "education"
    CERTIFICATIONS = "certifications"
    PROJECTS = "projects"
    OTHER = "other"

class ApplicationStatus(str, Enum):
    APPLIED = "APPLIED"
    IN_PROGRESS = "IN_PROGRESS"
    FIRST_ROUND_INTERVIEW = "FIRST_ROUND_INTERVIEW"
    FINAL_DECISION = "FINAL_DECISION"
    REJECTED = "REJECTED"
    HIRED = "HIRED"

class BillingCycle(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"

class PositionType(str, Enum):
    DATA_ANALYST = "data_analyst"
    FRONTEND_DEV = "frontend_dev"
    DATA_ENGINEER = "data_engineer"
    FULLSTACK_DEV = "fullstack_dev"
    NETWORK_ENGINEER = "network_engineer"
    BUSINESS_ANALYST = "business_analyst"
    PRODUCT_MANAGER = "product_manager"
    OTHER = "other"



class CreationMode(str, Enum):
    DIY = "diy"
    AI_AGENT = "ai_agent"
    CAREER_BUILDER = "career_builder"
    N8N = "n8n"

class ResumeStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    FINALIZED = "finalized"


#-----------------------------------------------------------------
class User_login(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    tenant_id: int

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_verified: Optional[bool] = None

class UserResponse(BaseModel):
    user_id: int
    email: str
    full_name: Optional[str]
    is_verified: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str
#-----------------------------------------------------------
class ResumeCreate(BaseModel):
    student_id: int
    creation_mode: Optional[CreationMode] = 'diy'
    position_type: PositionType 
    status: Optional[ResumeStatus] = 'draft'


class ResumeSectionInput(BaseModel):
    resume_id: Optional[int]
    section_type:SectionType
    content:dict
    

# -----------------------------------------------------------
class PostNewJob(BaseModel):
    tenant_id: int
    title:str
    company_name: str
    published_at: date #datetime.strptime('2025-04-14', '%Y-%m-%d').date()
    linkedin_url:Optional[str]
    apply_url: Optional[str]
    description: Optional[str] = None
    source: str = Field(default="manual")

class GetJobList(BaseModel):
    total_count: int
    total_pages: int
    current_page: int
    jobs: List[Job]

class NewApplication(BaseModel):
    student_id: int
    job_id: int
    recruiter_id : int
    resume_doc_url: str  

class PostMessage(BaseModel):
    sender_id : int
    receiver_id: int
    content: str

class PostMessageResponse(BaseModel):
    status:bool
    receiver_id:int

class AddSubscriptionPlan(BaseModel):
    name: str
    price_usd: float
    billing_cycle: BillingCycle
    features: dict
    is_active: bool = Field(default=True)


class AddSubscriptionUser(BaseModel):
    user_id : int
    plan_id : int
    payment_method : str
    payment_reference : str