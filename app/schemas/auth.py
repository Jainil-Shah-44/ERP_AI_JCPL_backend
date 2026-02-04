from pydantic import BaseModel

class LoginRequest(BaseModel):
    company_code: str
    username: str
    password: str
