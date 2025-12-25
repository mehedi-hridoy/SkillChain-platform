from fastapi import FastAPI
from app.api import events
from app.db.init_db import init_db

app = FastAPI(title="SkillChain Compliance API")

@app.on_event("startup")
def startup():
    init_db()

app.include_router(events.router)

@app.get("/")
def root():
    return {"status": "SkillChain backend running"}
