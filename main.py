from fastapi import FastAPI,Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from validationLayer import Base_asserts, Domains_url, UserInfo, EmailContent, MailResponse
from celery_ser import sendMail
from toolService import EmailService
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


if __name__=="__main__":
    uvicorn.run(app)