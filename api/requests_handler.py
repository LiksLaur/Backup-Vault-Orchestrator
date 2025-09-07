from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI, Depends
from authx import AuthXConfig, AuthX

app = FastAPI()
config = AuthXConfig()
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_TOKEN_LOCATION = ["cookies"]

security =  AuthX(config=config)

class SALogin(BaseModel):
    status_code: int
    status: str
    cookie_key: str
    input_password: str
    input_login: str
    access_token: str

class SUsersCreds(BaseModel):
    password: str
    login: str



@app.post('/login', response_model=SALogin)
def get_login_data(creds: SUsersCreds):
    token = security.create_access_token(uid="12345")
    return{
        "status_code": 200,
        "status": "successful",
        "cookie_key": "None",
        "input_password": creds.password,
        "input_login": creds.login,
        "access_token": token
    }
