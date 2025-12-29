from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from chat import router as chat_router
from auth_routes import router as auth_router
from meetings import router as meetings_router
from equipment import router as equipment_router
from tickets import router as tickets_router
from admin_superuser import router as admin_router
from config import settings 

app = FastAPI(title="Agentic IT Management Portal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(meetings_router, prefix="/api")
app.include_router(equipment_router, prefix="/api")
app.include_router(tickets_router, prefix="/api")
app.include_router(admin_router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok"}

