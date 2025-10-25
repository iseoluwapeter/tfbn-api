from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import SessionLocal, engine
from models import models
from models.models import Devotional
from typing import Annotated
from pydantic import BaseModel, Field
from utlis.cloudinary_config import *
from cloudinary.uploader import upload as cloudinary_upload



devotional_router = APIRouter()
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

dbDep = Annotated[Session, Depends(get_db)]






@devotional_router.get("/")
async def devotional(db:dbDep, skip: int =Query(0, ge=0), limit: int= Query(10, le=20)):
    devotionals = db.query(Devotional).order_by(desc(Devotional.date)).offset(skip).limit(limit).all()
    total = db.query(Devotional).count()

    return {
        "message": "Successfully fetched devotionals",
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": devotionals
    }

@devotional_router.get("/singledevotional/{uuid}")
async def devotional(db:dbDep, uuid:str):
    devotional = db.query(Devotional).filter(Devotional.uuid == uuid).first()

    if not devotional:
        raise HTTPException(status_code=404, detail="Devotional does not exist")
    
    result = [{
        "id": devotional.id,
        "title": devotional.title,
        "content": devotional.content,
        "scripture": devotional.scripture,
        "date": devotional.date,
        "image_url": devotional.image_url,
        "prayer": devotional.prayer,
        "reading": devotional.reading
    }]
    
    return result

@devotional_router.post("/")
async def devotional(
    db:dbDep, 
    title: str = Form(...), 
    content: str = Form(...), 
    date:str =Form(...), 
    scripture:str = Form(...), 
    image_url:UploadFile = File(...),
    prayer: str = Form(...),
    reading: str = Form(...)
    ):

    existing_devotional = db.query(Devotional).filter(Devotional.title == title).first()
    if existing_devotional:
        raise HTTPException(status_code=404, detail="not found")
    
    try:
        result = cloudinary_upload(image_url.file, folder="tfbn")
        imageUrl = result.get("secure_url")
    except Exception as e:
        raise HTTPException(status_code=500, detail="image upload filed")
    
    
    # devotional_details = devotional.dict()
    new_devotional = Devotional(
        title= title,
        content=content,
        date=date,
        scripture=scripture,
        image_url=imageUrl,
        prayer= prayer,
        reading=reading
    )
    db.add(new_devotional)
    db.commit()
    db.refresh(new_devotional)

    return{
        "message": "devotional successfully added",
        "new devotioanl": {
            "uuid": new_devotional.uuid,
            "title": new_devotional.title
        }
    }

@devotional_router.put("/")
async def devotional(db:dbDep, devotional_id: int, title: str = Form(...), 
    content: str = Form(...), 
    date:str =Form(...), 
    scripture:str = Form(...), 
    image_url:UploadFile = File(...),
    prayer: str = Form(...),
    reading: str = Form(...)):

    devotional = db.query(Devotional).filter(Devotional.id == devotional_id).first()

    if not devotional:
        raise HTTPException(status_code=404, detail="devotional does not exist")
    
    try:
        result = cloudinary_upload(image_url.file, folder="tfbn")
        imageUrl = result.get("secure_url")
    except Exception as e:
        raise HTTPException(status_code=500, detail="image upload filed")
    
    devotional.title = title
    devotional.content = content
    devotional.date = date
    devotional.scripture =scripture
    devotional.image_url = imageUrl
    devotional.prayer = prayer
    devotional.reading = reading

    db.commit()


    return {
        "message": f" {devotional.title} updated successfully",
        
    }

    




@devotional_router.delete("/")
async def devotional(db: dbDep, devotional: int):
    devotional = db.query(Devotional).filter(Devotional.id == devotional).first()

    if not devotional:
        raise HTTPException(status_code=404, detail="devotional does not exist")
    
    db.delete(devotional)
    db.commit()
    return{
        "message": "successfully deleted"
    }
