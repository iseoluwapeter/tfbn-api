from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import models
from models.models import Testimonies
from typing import Annotated
from pydantic import BaseModel, Field



testimony_router = APIRouter()
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

dbDep = Annotated[Session, Depends(get_db)]

class TestimonyCreate(BaseModel):
    testimony: str
    name: str
    location: str

@testimony_router.get("/")
async def testimony(db:dbDep):
    devotional = db.query(Testimonies).all()
    return devotional

@testimony_router.post("/")
async def testimony(db:dbDep, category:TestimonyCreate):
    
    testimony_credentials = category.dict()
    new_testimony = Testimonies(**testimony_credentials)

    db.add(new_testimony)
    db.commit()

    return{
        "message": "sucessfully added",
        "category": f"{new_testimony.name}"
    }

@testimony_router.put("/")
async def update_testimony(db:dbDep, testimony_id:int, testimony_data:TestimonyCreate):
    existing_testimony = db.query(Testimonies).filter(Testimonies.id == testimony_id).first()
   

    if not existing_testimony:
        raise HTTPException(status_code=404, detail="Testimony does not exist")
    
    existing_testimony.testimony = testimony_data.testimony
    existing_testimony.location = testimony_data.location
    existing_testimony.name = testimony_data.name

    db.commit()
    db.refresh(existing_testimony)

    return {
        "message": "Testimony sucessfully deleted",
        "testimony": existing_testimony.location
    }


@testimony_router.delete("/")
async def testimony(db:dbDep, testimony_id:int):
    testimony = db.query(Testimonies).filter(Testimonies.id == testimony_id).first()

    if not testimony:
        raise HTTPException(status_code=404, detail="Testimony does not exist")
    
    db.delete(testimony)
    db.commit()

    return {
        "message": "Testimony sucessfully deleted",
        "testimony": testimony.id
    }
