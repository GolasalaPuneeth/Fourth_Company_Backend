from langchain_openai import ChatOpenAI
import os
import getpass
from dotenv_vault import load_dotenv



load_dotenv()

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass(
        "Enter API key for OpenAI: ")
model = ChatOpenAI(
    model="gpt-4o", verbose=True).with_structured_output(method="json_mode")





# try:
#     validate(instance=ai_msg, schema=json_schema)
#     print("✅ AI response is valid and follows the schema.")
# except ValidationError as e:
#     print("❌ AI response is INVALID!")
#     print("Error:", e.message)
