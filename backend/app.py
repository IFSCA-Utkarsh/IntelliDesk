# backend/app.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from auth.routes import router as auth_router
from chat.routes import router as chat_router

app = FastAPI(title="IntelliDesk API")

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(auth_router, prefix="/api", tags=["Auth"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="IntelliDesk API",
        version="1.0.0",
        routes=app.routes,
    )

    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi
