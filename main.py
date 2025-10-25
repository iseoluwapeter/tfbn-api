from fastapi import FastAPI
from routes import devotional, events, admin, auth
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import uvicorn

app = FastAPI()

load_dotenv()

frontend_url = os.getenv("FRONTEND_URL")

app.add_middleware(
    CORSMiddleware,
    allow_origins = [frontend_url, "http://localhost:5173"],
    allow_credentials= True,
    allow_headers = ["*"],
    allow_methods = ["*"]
)



app.include_router(devotional.devotional_router, tags=["Devotional"], prefix="/devotional")
app.include_router(events.events_router, tags=["events"], prefix="/events")
app.include_router(admin.admin_router, tags=["admin"], prefix="/admin")
app.include_router(auth.auth_router, tags=["auth"], prefix="/auth")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

