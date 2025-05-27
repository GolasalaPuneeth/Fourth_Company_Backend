from datetime import datetime,date
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field, select
from sqlalchemy import Column, text, Enum as SQLAlchemyEnum # JSON, String, CheckConstraint, ForeignKey, 
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy import DateTime
import asyncio


DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_xQ6l9RdUzpcB@ep-square-glitter-a16us05k-pooler.ap-southeast-1.aws.neon.tech/Test_app"
async_engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

class TokenType(str, Enum):
    VERIFICATION = "verification"
    RESET = "reset"

class NotificationType(str, Enum):
    APPLICATION_STATUS = "application_status"
    NEW_MESSAGE = "new_message"
    SYSTEM = "system"
    PLAN_UPDATE = "plan_update"

class Tenant(SQLModel, table=True):
    __tablename__ = "tenants"
    tenant_id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    subdomain: Optional[str] = Field(max_length=100, unique=True)
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), 
        server_default=func.now(), 
        server_onupdate=func.now()
    ))
class User(SQLModel, table=True):
    __tablename__ = "users"
    user_id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenants.tenant_id")
    email: str = Field(max_length=255, unique=True)
    password_hash: str = Field(max_length=255)
    full_name: Optional[str] = Field(max_length=255)
    google_id: Optional[str] = Field(max_length=255)
    linkedin_id: Optional[str] = Field(max_length=255)
    is_verified: bool = Field(default=False)
    last_login: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True))
    )
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), 
        server_default=func.now(), 
        server_onupdate=func.now())
    )
class Role(SQLModel, table=True):
    __tablename__ = "roles"
    role_id: Optional[int] = Field(default=None, primary_key=True)
    role_name: str = Field(max_length=50, unique=True)

class UserRole(SQLModel, table=True):
    __tablename__ = "user_roles"
    user_id: int = Field(foreign_key="users.user_id", primary_key=True)
    role_id: int = Field(foreign_key="roles.role_id", primary_key=True)

class AuthToken(SQLModel, table=True):
    __tablename__ = "auth_tokens"
    token_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.user_id")
    token_type: TokenType
    token_value: str = Field(max_length=255)
    is_used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# -------------------- Resume Module --------------------

# class Resume(SQLModel, table=True):
#     __tablename__ = "resumes"
    
#     resume_id: Optional[int] = Field(default=None, primary_key=True)
#     student_id: int = Field(foreign_key="users.user_id")
#     career_specialist_id: Optional[int] = Field(foreign_key="users.user_id")
#     file_url: Optional[str] = Field(max_length=255)
#     raw_content: Optional[str] = None
#     json_content: Optional[dict] = Field(
#         sa_column=Column(JSONB)  # Proper JSONB specification
#     )
#     creation_mode: CreationMode  = Field(
#     sa_column=Column(SQLAlchemyEnum(CreationMode, name="creation_mode"))
# )
#     status: ResumeStatus = Field(default=ResumeStatus.DRAFT)
#     position_type: Optional[PositionType] = None
#     created_at: datetime = Field(
#         sa_column=Column(DateTime(timezone=True), server_default=text("NOW()"))
#     )
#     updated_at: Optional[datetime] = Field(
#         sa_column=Column(DateTime(timezone=True), onupdate=text("NOW()"))
#     )

class Resume(SQLModel, table=True):
    __tablename__ = "resumes"
    
    resume_id: Optional[int] = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"server_default": "GENERATED ALWAYS AS IDENTITY"}
    )
    student_id: int = Field(foreign_key="users.user_id")
    career_specialist_id: Optional[int] = Field(foreign_key="users.user_id")
    file_url: Optional[str] = Field(max_length=255)
    raw_content: Optional[str] = None
    json_content: Optional[dict] = Field(sa_column=Column(JSONB))
    creation_mode: str = Field(default='diy')
    status: str = Field(default='draft')
    position_type: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# class ResumeSection(SQLModel, table=True):
#     __tablename__ = "resume_sections"
#     section_id: Optional[int] = Field(default=None, primary_key=True)
#     resume_id: int = Field(foreign_key="resumes.resume_id")
#     section_type: SectionType
#     content: dict = Field(sa_column=Column(JSONB))
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     updated_at: datetime = Field(default_factory=datetime.utcnow)

class ResumeSection(SQLModel, table=True):
    __tablename__ = "resume_sections"
    
    section_id: Optional[int] = Field(default=None, primary_key=True)
    resume_id: int = Field(foreign_key="resumes.resume_id")
    section_type: str
    content: dict = Field(
        sa_column=Column(JSONB)  # Proper JSONB specification
    )
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=text("NOW()"))
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"))
    )

class Keyword(SQLModel, table=True):
    __tablename__ = "keywords"
    keyword_id: Optional[int] = Field(default=None, primary_key=True)
    position_type: Optional[str] = Field(max_length=50)
    keyword: str = Field(max_length=100)
    category: str = Field(max_length=30)

class ResumeKeyword(SQLModel, table=True):
    __tablename__ = "resume_keywords"
    resume_id: int = Field(foreign_key="resumes.resume_id", primary_key=True)
    keyword_id: int = Field(foreign_key="keywords.keyword_id", primary_key=True)

# -------------------- Job Applications Module --------------------
class Job(SQLModel, table=True):
    __tablename__ = "jobs"
    job_id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenants.tenant_id")
    title: str = Field(max_length=255)
    company_name: Optional[str] = Field(max_length=255)
    description: Optional[str] = None
    published_at: Optional[datetime] = None
    linkedin_url: Optional[str] = Field(max_length=255)
    apply_url: Optional[str] = Field(max_length=255)
    source: str = Field(default="manual")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Application(SQLModel, table=True):
    __tablename__ = "applications"
    application_id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="users.user_id")
    job_id: int = Field(foreign_key="jobs.job_id")
    recruiter_id: Optional[int] = Field(foreign_key="users.user_id")
    resume_doc_url: Optional[str] = Field(max_length=255)
    resume_pdf_url: Optional[str] = Field(max_length=255)
    status: Optional[str] = 'applied'
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class RecruiterAssignment(SQLModel, table=True):
    __tablename__ = "recruiter_assignments"
    assignment_id: Optional[int] = Field(default=None, primary_key=True)
    recruiter_id: int = Field(foreign_key="users.user_id")
    student_id: int = Field(foreign_key="users.user_id")
    assigned_by: Optional[int] = Field(foreign_key="users.user_id")
    status: str = Field(default="working")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# -------------------- Messaging Module --------------------
class Message(SQLModel, table=True):
    __tablename__ = "messages"
    message_id: Optional[int] = Field(default=None, primary_key=True)
    sender_id: int = Field(foreign_key="users.user_id")
    receiver_id: int = Field(foreign_key="users.user_id")
    content: str
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    is_read: bool = Field(default=False)

class Notification(SQLModel, table=True):
    __tablename__ = "notifications"
    notification_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.user_id")
    message: str
    type: NotificationType = Field(default="system")
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# -------------------- Candidate Management Module --------------------
class CandidateReview(SQLModel, table=True):
    __tablename__ = "candidate_reviews"
    review_id: Optional[int] = Field(default=None, primary_key=True)
    recruiter_id: int = Field(foreign_key="users.user_id")
    application_id: int = Field(foreign_key="applications.application_id")
    rating: Optional[int] = None
    comments: Optional[str] = None
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)

class CandidateTag(SQLModel, table=True):
    __tablename__ = "candidate_tags"
    tag_id: Optional[int] = Field(default=None, primary_key=True)
    tag_name: str = Field(max_length=50, unique=True)

class ApplicationTag(SQLModel, table=True):
    __tablename__ = "application_tags"
    application_id: int = Field(foreign_key="applications.application_id", primary_key=True)
    tag_id: int = Field(foreign_key="candidate_tags.tag_id", primary_key=True)

# -------------------- Admin & Subscriptions Module --------------------
class SubscriptionPlan(SQLModel, table=True):
    __tablename__ = "subscription_plans"
    plan_id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    price_usd: float
    billing_cycle: str = Field(default="monthly")
    features: dict = Field(sa_column=Column(JSONB))
    is_active: bool = Field(default=True)

class UserSubscription(SQLModel, table=True):
    __tablename__ = "user_subscriptions"
    subscription_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.user_id")
    plan_id: int = Field(foreign_key="subscription_plans.plan_id")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ends_at: Optional[datetime] = None
    is_cancelled: bool = Field(default=False)
    payment_method: Optional[str] = Field(max_length=50)
    payment_reference: Optional[str] = Field(max_length=255)

class AdminLog(SQLModel, table=True):
    __tablename__ = "admin_logs"
    log_id: Optional[int] = Field(default=None, primary_key=True)
    admin_id: int = Field(foreign_key="users.user_id")
    action: str = Field(max_length=255)
    affected_table: str = Field(max_length=50)
    record_id: Optional[int] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
#--------------------------------------------------------------------------------
async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)