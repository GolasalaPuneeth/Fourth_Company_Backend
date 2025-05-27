from fastapi import FastAPI,Depends, HTTPException, status, File, UploadFile, WebSocket, WebSocketDisconnect,APIRouter,Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from validationLayer import *
from celery_ser import sendMail,extract_and_convert_to_json
from sqlmodel import select
from DataBase import InsertLogError
from clientsService import celery_app
from resume_builder import ATS_builder
from toolService import *
from TMTdb_schemas import *
import asyncio
import tempfile, os
import Sample_Data
import uvicorn

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
auth_scheme = HTTPBearer()


VALID_TOKEN = "supersecrettoken"

def validate_token(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    if credentials.credentials != VALID_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return credentials.credentials


@app.websocket("/ws/result/dev/{task_id}")
async def websocket_task_status(websocket: WebSocket, task_id: str):
    await websocket.accept()
    try:
        while True:
            result = celery_app.AsyncResult(task_id)
            status = result.state

            if status == "PENDING":
                await websocket.send_json({"status": "Pending"})
            elif status == "STARTED":
                await websocket.send_json({"status": "In Progress"})
            elif status == "SUCCESS":
                await websocket.send_json({"status": "Completed"})
                break
            elif status == "FAILURE":
                await websocket.send_json({"status": "Failed", "reason": str(result.info)})
                break
            else:
                await websocket.send_json({"status": status})

            await asyncio.sleep(1.5)  # Polling interval

    except WebSocketDisconnect:
        print(f"Client disconnected from task {task_id}")
    except Exception as e:
        await websocket.send_json({"status": "Error", "reason": str(e)})
        await websocket.close()


@app.get("/")
async def base_asserts(token: str = Depends(validate_token),response_model = list[Base_asserts]):
    return Sample_Data.base_Asserts


@app.get("/Domains_url")
async def Domain_URL(token: str = Depends(validate_token),response_model = list[Domains_url]):
    return Sample_Data.Domains_Url

@app.post("/mail_Service")
async def Mail_service(UserInput : UserInfo,token: str = Depends(validate_token),response_model = list[MailResponse]):
    Pre_process = {
        "SUBJECT": f"New Application: {UserInput.FULLNAME}",
        "BODY_TEXT": f"New Application: {UserInput.FULLNAME}",
        "BODY_HTML": f"""
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>New Contact Form Submission</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
        <tr>
            <td style="padding: 20px; background-color: #0066cc; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 24px;">New Contact Form Submission</h1>
            </td>
        </tr>
        <tr>
            <td style="padding: 20px;">
                <p style="margin: 0 0 20px 0; color: #333333; font-size: 16px;">A new contact form submission has been received from website.</p>
                
                <table cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse;">
                    <tr>
                        <td style="padding: 10px; background-color: #f8f8f8; border: 1px solid #dddddd; width: 120px;">
                            <strong style="color: #333333;">Full Name:</strong>
                        </td>
                        <td style="padding: 10px; border: 1px solid #dddddd;">
                            {UserInput.FULLNAME}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; background-color: #f8f8f8; border: 1px solid #dddddd;">
                            <strong style="color: #333333;">Phone:</strong>
                        </td>
                        <td style="padding: 10px; border: 1px solid #dddddd;">
                            {UserInput.PHONE}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; background-color: #f8f8f8; border: 1px solid #dddddd;">
                            <strong style="color: #333333;">Email:</strong>
                        </td>
                        <td style="padding: 10px; border: 1px solid #dddddd;">
                            <a href="mailto:{UserInput.EMAIL_client}" style="color: #0066cc; text-decoration: none;">{UserInput.EMAIL_client}</a>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; background-color: #f8f8f8; border: 1px solid #dddddd;">
                            <strong style="color: #333333;">Message:</strong>
                        </td>
                        <td style="padding: 10px; border: 1px solid #dddddd;">
                            {UserInput.MESSAGE}
                        </td>
                    </tr>
                </table>

                <p style="margin: 20px 0 0 0; color: #666666; font-size: 14px;">This inquiry was received from {UserInput.SOURCE}</p>
            </td>
        </tr>
        <tr>
            <td style="padding: 20px; background-color: #f8f8f8; text-align: center; border-top: 1px solid #dddddd;">
                <p style="margin: 0; color: #666666; font-size: 14px;">Please respond to this inquiry within 24 hours.</p>
            </td>
        </tr>
    </table>
</body>"""
    }
    obj1 = EmailService(EmailContent(**Pre_process))
    result = await obj1.EmailFormat()
    if(sendMail.delay(result).get()):
        return  [MailResponse(mail_status = True)]
    raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SomeThing Went Wrong",
        )

@app.post("/upload/dev")
async def upload_file(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[-1].lower()
    if ext not in [".pdf", ".docx"]:
        raise HTTPException(status_code=400, detail="Only PDF or DOCX allowed")

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    task = extract_and_convert_to_json.delay(tmp_path, ext.lstrip("."))
    return {"task_id": task.id, "message": "Processing started"}
    
@app.get("/result/dev/{task_id}")
async def get_result(task_id: str):
    res = celery_app.AsyncResult(task_id)
    if res.state == "PENDING":
        return {"status": "Pending"}
    elif res.state == "SUCCESS":
        return {"status": "Completed", "data": res.result}
    elif res.state == "FAILURE":
        return {"status": "Failed", "reason": str(res.info)}
    return {"status": res.state}


@app.post("/logger/{Error_type}")
async def Logger_Notifier(Error_type:Status,payload:logger_info): #Error :logger_info,
    if Error_type.value == "INFO":
        await InsertLogError(Error_type.value,f"{payload.Service} and {payload.Error_info}")
        return {"Status":True}
    if Error_type.value == "WARNING":
        await InsertLogError(Error_type.value,f"{payload.Service} and {payload.Error_info}")
        return {"Status":True}
    if Error_type.value == "CRITICAL":
        await InsertLogError(Error_type.value,f"{payload.Service} and {payload.Error_info}")
        data = EmailContent(SENDER="puneeth3sprime@gmail.com",RECIPIENT="puneeth3sprime@gmail.com",
                            SUBJECT=f"Error from {payload.Service}",
                            BODY_TEXT="service Down", BODY_HTML=f"<h1>{payload.Error_info}</h1>")
        Report = await EmailService(data).EmailFormat()
        if(sendMail.delay(Report).get()):
            return  [MailResponse(mail_status = True)]
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SomeThing Went Wrong",
            )
    return {"status": "ok"}


# -----------------------------------------------------

auth_router = APIRouter(prefix="/auth", tags=["AUTHENTICATION"])
resume_router = APIRouter(prefix="/resumes", tags=["RESUMES BUILDER"])
job_router = APIRouter(prefix="/jobs", tags=["JOB APPLICATION"])
message_router = APIRouter(prefix="/messages", tags=["MESSAGING & NOTIFICATIONS"])
candidate_management_router = APIRouter(prefix="/candidatemgmt",tags = ["CANDIDATE MANAGEMENT"]) 
plans_router = APIRouter(prefix="/plans",tags=["PLANS"])
subscription_router = APIRouter(prefix="/subscriptions",tags=["SUBSCRIPTIONS"])
# ---------------------------------------------------------
@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    # Check for existing user
    async with async_session_maker() as session:
        existing_user = await session.execute(select(User).where(User.email == user.email))
        existing_user = existing_user.scalars().first()        
        if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered"
                )
    
        # Create new user
        hashed_password = user.password
        db_user = User(
            email=user.email,
            password_hash=hashed_password,
            full_name=user.full_name,
            tenant_id=user.tenant_id,
            is_verified=False,
            created_at=datetime.utcnow()
        )
        try:
            session.add(db_user)
            await session.commit()
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{e}")
        return db_user
    


@auth_router.post("/login", response_model=Token)
async def login_user_endpoint(
    form_data: User_login
):
    async with async_session_maker() as session:
        user = await session.execute(select(User).where(User.email == form_data.email))
        existing_user = user.scalars().first()
        if not existing_user:
            return Token(access_token="testing_class",token_type="testing").model_dump()
        return Token(access_token=existing_user.email,token_type=existing_user.password_hash).model_dump()


@auth_router.get("/users/{user_id}", response_model=User)
async def get_user_endpoint(user_id: int):
    async with async_session_maker() as session:
        user = await session.execute(select(User).where(User.user_id == user_id))
        existing_user = user.scalars().first()
        if not existing_user:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return existing_user

@auth_router.put("/users/{user_id}", response_model=User)
async def update_user_endpoint(
    user_id: int,
    update_data: UserUpdate):
    current_user = await get_user_data(user_id)
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    async with async_session_maker() as session:
        current_user.full_name = update_data.full_name
        current_user.is_verified = update_data.is_verified
        session.add(current_user)
        await session.commit()
        return current_user
    
@auth_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(user_id: int):
    current_user = await get_user_data(user_id)
    if not current_user:
                raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    async with async_session_maker() as session:
        await session.delete(current_user)
        await session.commit()
        return

@resume_router.post("", response_model=bool,status_code=status.HTTP_201_CREATED)
async def create_resume(resume_data: ResumeCreate):
    resume_info = Resume(**resume_data.model_dump())
    async with async_session_maker() as session:
        try:
            session.add(resume_info)
            await session.commit()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{e.__dict__}"
            )
    return True

@resume_router.get("/{resume_id}",response_model=Resume)
async def get_resume(resume_id:int):
    return await get_resume_data(resume_id)

@resume_router.put("/{resume_id}",response_model=bool)
async def update_resume(resume_id:int,update_data:ResumeCreate):
    resume_data =  await get_resume_data(resume_id)
    resume_data.student_id = update_data.student_id
    resume_data.creation_mode = update_data.creation_mode
    resume_data.position_type = update_data.position_type
    resume_data.status = update_data.status
    async with async_session_maker() as session:
        session.add(resume_data)
        await session.commit()
        return True

@resume_router.delete("/{resume_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(resume_id: int):
    resume_data = await get_resume_data(resume_id)
    if not resume_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"resume not found with {resume_id}")
    async with async_session_maker() as session:
        await session.delete(resume_data)
        await session.commit()

@resume_router.post("/{resume_id}/section",response_model=ResumeSection)
async def add_resume_section(resume_id:int,section_payload:ResumeSectionInput):
    section_payload.resume_id=resume_id
    resume_section = ResumeSection(**section_payload.model_dump())
    async with async_session_maker() as session:
        try:
            session.add(resume_section)
            await session.commit()
            return resume_section
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{e.orig}")

@resume_router.put("/section/{section_id}",response_model=ResumeSection,status_code=status.HTTP_200_OK)
async def update_section(section_id:int,section_payload:ResumeSectionInput):
    async with async_session_maker() as session:
        try:
            resume_section = await session.execute(select(ResumeSection).where(ResumeSection.section_id==section_id))
            resume_section = resume_section.scalars().first()
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{e}")
        if not resume_section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,detail=f"record not found with {section_id}"
            )
        resume_section.section_type = section_payload.section_type
        resume_section.content = section_payload.content
        session.add(resume_section)
        await session.commit()
        return resume_section
    
@resume_router.delete("/section/{section_id}",status_code=status.HTTP_204_NO_CONTENT)
async def remove_section(section_id:int):
    async with async_session_maker() as session:
        try:
            resume_section = await session.execute(select(ResumeSection).where(ResumeSection.section_id==section_id))
            resume_section = resume_section.scalars().first()
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{e}")
        if not resume_section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,detail=f"record not found with {section_id}"
            )
        await session.delete(resume_section)
        await session.commit()
        

@job_router.post("",response_model= bool)
async def post_new_job(job_data: PostNewJob):
    job = Job(**job_data.model_dump())
    async with async_session_maker() as session:
        session.add(job)
        await session.commit()
        return True
    
@job_router.get("",response_model=GetJobList)
async def get_items(
    page: int = Query(1, ge=1)
):
    page_size = 10
    offset = (page - 1) * page_size
    statement = (
        select(Job)
        .order_by(Job.published_at.desc())  # reverse order: latest first
        .offset(offset)
        .limit(page_size)
    )
    async with async_session_maker() as session:
        count_result = await session.execute(select(func.count()).select_from(Job))
        total_count = count_result.scalar_one()
        total_pages = (total_count + page_size - 1) 
        results = await session.execute(statement)
        data = (results.scalars().all())
        return GetJobList(
            total_count=total_count,
            total_pages=total_pages,
            current_page=page,
            jobs=data
        )
@job_router.get("/{job_id}",response_model=Job)
async def Job_detail(job_id: int):
    async with async_session_maker() as session:
        job = await session.execute(select(Job).where(Job.job_id == job_id))
        Job_details = job.scalars().first()
        if not Job_details:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job_details not found"
        )
    return Job_details

@job_router.delete("/{job_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: int):
    job_record = await Job_detail_helper(job_id)
    async with async_session_maker() as session:
        await session.delete(job_record)
        await session.commit()
        return

@job_router.post("/applications",response_model= bool)
async def apply_to_job(application_data: NewApplication):
        data = Application(**application_data.model_dump())
        async with async_session_maker() as session:
            session.add(data)
            await session.commit()
            return True
        
@job_router.get("/applications/{application_id}",response_model= Application)
async def get_application(application_id:int):
        data = await get_application_data(application_id)
        if not data:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
        return data


@job_router.put("/applications/{application_id}",response_model = Application)
async def update_application_status(application_id:int,status:ApplicationStatus):
        data = await get_application_data(application_id)
        if not data:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
        data.status = status.lower()
        async with async_session_maker() as session:
            session.add(data)
            await session.commit() 
        return data

@job_router.delete("/applications/{application_id}",status_code=status.HTTP_204_NO_CONTENT)
async def withdraw_application(application_id:int):
        data = await get_application_data(application_id)
        if not data:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
        async with async_session_maker() as session:
            await session.delete(data)
            await session.commit() 


@message_router.post("",response_model= PostMessageResponse)
async def send_message(message_data: PostMessage):
    message_data = Message(**message_data.model_dump())
    async with async_session_maker() as session:
        session.add(message_data)
        await session.commit()
        return PostMessageResponse(status=True,receiver_id=message_data.receiver_id)

@plans_router.get("",response_model=list[SubscriptionPlan])
async def list_all_plans():
    plan = select(SubscriptionPlan)
    async with async_session_maker() as session:
        plans = await session.execute(plan)
        return(plans.scalars().all())

@plans_router.post("")
async def create_plan(plan: AddSubscriptionPlan):
    plan = SubscriptionPlan(**plan.model_dump())
    async with async_session_maker() as session:
        session.add(plan)
        await session.commit()

@plans_router.put("/{plan_id}")
async def update_plan(plan_id: int, payload:AddSubscriptionPlan):
    async with async_session_maker() as session:
        record = await session.execute(select(SubscriptionPlan).where(SubscriptionPlan.plan_id == plan_id))
        plan_data = record.scalars().first()
        plan_data.name = payload.name
        plan_data.price_usd = payload.price_usd
        plan_data.billing_cycle = payload.billing_cycle
        plan_data.features = payload.features
        plan_data.is_active = payload.is_active
        await session.commit()

@plans_router.delete("/{plan_id}")
async def delete_plan(plan_id: int):
    async with async_session_maker() as session:
        record = await session.execute(select(SubscriptionPlan).where(SubscriptionPlan.plan_id == plan_id))
        plan_data = record.scalars().first()
        await session.delete(plan_data)
        await session.commit()

@subscription_router.post("",response_model=AddSubscriptionUser,status_code=status.HTTP_201_CREATED)
async def Assign_plan_to_user(sub_data: AddSubscriptionUser):
    data = UserSubscription(**sub_data.model_dump())
    async with async_session_maker() as session:
        try:
            session.add(data)
            await session.commit()
            return sub_data
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{e}")

@subscription_router.get("/{User_id}",response_model=UserSubscription,status_code=status.HTTP_200_OK)
async def view_user_subscription(User_id : int):
    async with async_session_maker() as session:
        try:
            user_subscription = await session.execute(select(UserSubscription).where(UserSubscription.user_id==User_id))
            user_subscription = user_subscription.scalars().first()
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{e}")
        if not user_subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,detail=f"record not found with {User_id}"
            )
        return user_subscription
    
@subscription_router.delete("/{User_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_subscription(User_id : int):
    async with async_session_maker() as session:
        try:
            user_subscription = await session.execute(select(UserSubscription).where(UserSubscription.user_id==User_id))
            user_subscription = user_subscription.scalars().first()
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"{e}")
        if not user_subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,detail=f"record not found with {User_id}"
            )
        await session.delete(user_subscription)
        await session.commit()
#-----------------------------------------------------------------------------------------------
app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(job_router)
app.include_router(message_router)
app.include_router(candidate_management_router)
app.include_router(plans_router)
app.include_router(subscription_router)
app.include_router(ATS_builder)

if __name__=="__main__":
    uvicorn.run(app)