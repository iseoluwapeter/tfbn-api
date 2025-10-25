from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File, Query
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import models
from models.models import Events
from typing import Annotated
from pydantic import BaseModel, Field
from utlis.cloudinary_config import *
from cloudinary.uploader import upload as cloudinary_upload


events_router = APIRouter()
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

dbDep = Annotated[Session, Depends(get_db)]


@events_router.get("/")
async def events(db:dbDep):
    devotional = db.query(Events).all()
    return devotional


@events_router.post("/")
async def events(
    db:dbDep, 
    title: str = Form(...), 
    date:str =Form(...), 
    image_url:UploadFile = File(...),
    ):

    existing_events = db.query(Events).filter(Events.title == title).first()
    if existing_events:
        raise HTTPException(status_code=404, detail="not found")
    
    try:
        result = cloudinary_upload(image_url.file, folder="tfbn/events")
        imageUrl = result.get("secure_url")
    except Exception as e:
        raise HTTPException(status_code=500, detail="image upload filed")
    
    

    new_event = Events(
        title= title,
        date=date,
        image_url=imageUrl,
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return{
        "message": "devotional successfully added",
        "new devotioanl": {
            "uuid": new_event.id,
            "title": new_event.title
        }
    }

@events_router.put("/")
async def events(db:dbDep, event_id: int, date: str =Form(...),title: str=Form(...), image_url:UploadFile =File(...)):
    event = db.query(Events).filter(Events.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="devotional does not exist")
    
    try:
        result = cloudinary_upload(image_url.file, folder="tfbn/events")
        imageUrl = result.get("secure_url")
    except Exception as e:
        raise HTTPException(status_code=500, detail="image upload filed")
    
    event.date = date
    event.title = title
    event.image_url = imageUrl

    db.commit()
    db.refresh(event)

    return{
        "message": f" {event.id} updated sucessfully",
        "event": event
    }




@events_router.delete("/")
async def events(db: dbDep, event: int):
    event = db.query(Events).filter(Events.id == event).first()

    if not event:
        raise HTTPException(status_code=404, detail="devotional does not exist")
    
    db.delete(event)
    db.commit()
    return{
        "message": "successfully deleted"
    }