from validationLayer import EmailContent
from fastapi import HTTPException,status
from TMTdb_schemas import *
class EmailService():
    def __init__(self, emailcontext: EmailContent):
        self.emailcontext = emailcontext

    async def EmailFormat(self):
        return {
            "Source": self.emailcontext.SENDER,
            "Destination": {"ToAddresses": [self.emailcontext.RECIPIENT]},
            "Message": {
                "Subject": {"Data": self.emailcontext.SUBJECT},
                "Body": {
                    "Text": {"Data": self.emailcontext.BODY_TEXT},
                    "Html": {"Data": self.emailcontext.BODY_HTML},
                },
            },
        }
async def get_user_data(user_id: int):
    async with async_session_maker() as session:
        user = await session.execute(select(User).where(User.user_id == user_id))
        existing_user = user.scalars().first()
    return existing_user

async def Job_detail_helper(job_id: int):
    async with async_session_maker() as session:
        job = await session.execute(select(Job).where(Job.job_id == job_id))
        Job_details = job.scalars().first()
        if not Job_details:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job_details not found"
        )
    return Job_details

async def get_application_data(application_id: int):
    async with async_session_maker() as session:
        application = await session.execute(select(Application).where(Application.application_id == application_id))
        application_data = application.scalars().first()
    return application_data

async def get_resume_data(resume_id: int):
    async with async_session_maker() as session:
        resume_data = await session.execute(select(Resume).where(Resume.resume_id == resume_id))
        resume = resume_data.scalars().first()
    return resume