from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File, Query
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import models
from models.models import Article
from typing import Annotated, Optional
from pydantic import BaseModel, Field
from utlis.cloudinary_config import *
from cloudinary.uploader import upload as cloudinary_upload
from slugify import slugify
from datetime import datetime



article_router = APIRouter()
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

dbDep = Annotated[Session, Depends(get_db)]

class ArticleCreate(BaseModel):
    title: str
    author: str
    content: str
    cover_image:str
    category: str
    is_published: str 


@article_router.get("/")
async def article(db:dbDep, page: int = Query(1, ge=1), limit: int =Query(4, le=20), search: Optional[str] = None):
    skip = (page -1) * limit

    query = db.query(Article)

    if search:
        query = query.filter(Article.title.ilike(f"%{search}"))

    total_articles =query.count()

    articles = query.order_by(Article.created_at.desc()).offset(skip).limit(limit).all()


    total_pages = (total_articles + limit -1) // limit

    data = []

    for article in articles:
        data.append({
            "id": article.id,
            "title": article.title,
            "slug": article.slug,
            "cover_image": article.cover_image,
            "author": article.author,
            "content": article.content,
            "category_id": article.category_id,
            "is_published": article.is_published,
            "updated_at": article.updated_at,
            "created_at": article.created_at
        })

    return {
        "message": "Sucessfully fecthed articles",
         "pagination": {
            "total": total_articles,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
        "data": data
    }

@article_router.get("/detail/{slug}")
async def article(db:dbDep, slug:str):
    article = db.query(Article).filter(Article.slug ==slug).first()

    if not article:
         raise HTTPException(status_code=404, detail="Article does not exist")
    
    result = [{
        "id": article.id,
        "title": article.title,
        "slug": article.slug,
        "content": article.content,
        "author": article.author,
        "category": article.category,
        "cover_img": article.cover_image,
        "created_at": article.created_at,
        "updated_at": article.updated_at,
        # "published_at": article.published_at
    }]
    
    return result

@article_router.get("/articles")
async def article(db:dbDep, category_id:int, page:int=Query(1, le=20), limit:int =Query(4 ,le=20)):
    skip = (page -1) * limit

    query = db.query(Article).filter(Article.category_id == category_id)

    total_articles = query.count()

    articles = query.order_by(Article.created_at.desc()).offset(skip).limit(limit).all()

    total_pages =(total_articles + limit -1) // limit

    return {
        "message": "Sucessfully fecthed articles",
         "pagination": {
            "total": total_articles,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
        "data": articles
    }   

@article_router.post("/")
async def article(db:dbDep, title: str = Form(...),
    author: str = Form(...),
    content: str = Form(...),
    cover_image:UploadFile = File(...),
    category_id: int = Form(...),
    is_published: bool = Form(...)):

    existing_article = db.query(Article).filter(Article.title == title).first()

    if existing_article:
        raise HTTPException(status_code=404, detail="article already existed")
    
    try:
        result = cloudinary_upload(cover_image.file, folder="tfbn/article")
        imageUrl = result.get("secure_url")
    except Exception as e:
        raise HTTPException(status_code=500, detail="image upload failed")

    slug=slugify(title)

    new_article = Article(
        title=title,
        author=author,
        content=content,
        cover_image=imageUrl,
        category_id=category_id,
        slug=slug,
        is_published=is_published,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        # published_at=datetime.utcnow() if is_published else None
    )
    db.add(new_article)
    db.commit()
    db.refresh(new_article)

    return{
        "messgae": "article created",
        "title": f" {new_article.title}"
    }


@article_router.put("/")
async def article(db:dbDep, article_id: int, 
    title: str = Form(...),               
    content: str = Form(...), 
    author:str =Form(...),
    created_at:str =Form(...), 
    cover_image:UploadFile = File(...),
):

    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="devotional does not exist")
    
    # Convert dd/mm/yyyy to datetime
    try:
        parsed_date = datetime.strptime(created_at, "%d/%m/%Y")
    except ValueError:
        raise HTTPException(status_code=400, detail="Date must be in dd/mm/yyyy format")
    
    try:
        result = cloudinary_upload(cover_image.file, folder="tfbn")
        imageUrl = result.get("secure_url")
    except Exception as e:
        raise HTTPException(status_code=500, detail="image upload filed")
    
    article.title = title
    article.content = content
    article.author = author
    article.created_at = parsed_date
    article.cover_image = imageUrl


    db.commit()


    return {
        "message": f" {article.title} updated successfully",  
    }

@article_router.delete("/")
async def devotional(db: dbDep, article: int):
    article = db.query(Article).filter(Article.id == article).first()

    if not article:
        raise HTTPException(status_code=404, detail="devotional does not exist")
    
    db.delete(article)
    db.commit()
    return{
        "message": "successfully deleted"
    }
