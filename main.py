from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import json
import os
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

DB_FILE = "database.json"

# Create database file
if not os.path.exists(DB_FILE):

    data = {
        "users": [],
        "detections": []
    }

    with open(DB_FILE, "w") as f:
        json.dump(data, f)


def read_db():
    with open(DB_FILE, "r") as f:
        return json.load(f)


def write_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ======================
# Pages
# ======================

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request}
    )


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):

    username = request.query_params.get("username", "User")

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "username": username
        }
    )


# ======================
# API
# ======================

@app.post("/register")
async def register(request: Request):

    body = await request.json()

    db = read_db()

    user = {
        "name": body["name"],
        "email": body["email"],
        "password": body["password"]
    }

    db["users"].append(user)

    write_db(db)

    return {"message": "Registered Successfully"}


@app.post("/login")
async def login(request: Request):

    body = await request.json()

    email = body["email"]
    password = body["password"]

    db = read_db()

    for user in db["users"]:

        if user["email"] == email and user["password"] == password:

            return {
                "message": "Login Success",
                "name": user["name"]
            }

    return {"message": "Invalid Credentials"}


@app.post("/detect")
async def detect(request: Request):

    body = await request.json()

    db = read_db()

    detection = {
        "device": body["device"],
        "status": body["status"],
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    db["detections"].append(detection)

    write_db(db)

    return {"message": "Detection Saved"}


@app.get("/detections")
def detections():

    db = read_db()

    return db["detections"][::-1]