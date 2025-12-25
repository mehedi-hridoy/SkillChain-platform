from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import auth, events, products, batches, dpp, upload, demo_requests, compliance, content
from app.db.init_db import init_db
import os

app = FastAPI(title="SkillChain Compliance API", description="EU DPP-compliant supply chain transparency platform")

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
uploads_dir = "uploads"
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/files", StaticFiles(directory=uploads_dir), name="files")

@app.on_event("startup")
def startup():
    init_db()

app.include_router(auth.router)
app.include_router(events.router)
app.include_router(products.router)
app.include_router(batches.router)
app.include_router(dpp.router)
app.include_router(upload.router)
app.include_router(demo_requests.router)
app.include_router(compliance.router)
app.include_router(content.router)

@app.get("/")
def root():
    return {"status": "SkillChain backend running"}
