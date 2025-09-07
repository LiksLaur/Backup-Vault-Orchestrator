from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI, Depends

app = FastAPI()

class SRegistration(BaseModel):
    status_code: int
    status: str
    cookie_key: str
    input_password: str
    input_login: str



@app.get('/link', response_model=SRegistration)
def get_regestrarion_data(password: str, login: str):
    return{
        "status_code": 200,
        "status": "successful",
        "cookie_key": "None",
        "input_password": password,
        "input_login": login
    }
