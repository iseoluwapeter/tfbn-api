from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import models
from models.models import Comments, Article
from typing import Annotated
from pydantic import BaseModel, Field

comment_router = APIRouter()
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

dbDep = Annotated[Session, Depends(get_db)]

class CommentCreate(BaseModel):
    name: str
    email: str
    comment: str

@comment_router.post("/")
async def comment(db:dbDep, comment:CommentCreate, article_id: int):
    
    article = db.query(Article).filter(Article.id == article_id).first()

    if not article:
        raise HTTPException(status_code=404, detail="article does not exist")
    
    new_comment = Comments(
        name=comment.name,
        email=comment.email,
        comment=comment.comment,
        article_id=article_id,
        is_approved=False, 
        is_read=False
    )

    db.add(new_comment)
    db.commit()

    return {
        "message": "Comment added successfully. Pending admin approval.",
        "notification": f"{new_comment.name} made a new comment on '{article.title}'"
    }


@comment_router.get("/article/{article_id}")
async def get_comments_for_article(article_id: int, db: dbDep):
    comments = (
        db.query(Comments)
        .filter(
            Comments.article_id == article_id,
            Comments.is_approved == True
        )
        .all()
    )

    return {
        "article_id": article_id,
        "comments": comments
    }

@comment_router.get("/pending")
async def get_unapproved_comments(db: dbDep, page: int =Query(1, ge=1), limit: int = Query(10, le=20)):
    skip = (page -1) * limit

    query = db.query(Comments).filter(Comments.is_approved == False)

    pending = query.order_by(Comments.created_at.desc()).offset(skip).limit(limit).all()

    total_pending = query.count()
    total_pages = (total_pending + limit -1) //limit

  

    return {
        "message": "Successfuly fetched pending comments",
        "pagination": {
            "total": total_pending,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page >1,
        },
        "pending_comments": pending,

    }

@comment_router.get("/approve/{comment_id}")
async def approve_comments(db:dbDep, comment_id: int):
    approve_comment = db.query(Comments).filter(Comments.id == comment_id).first()

    if not approve_comment:
        raise HTTPException(status_code=404, detail="comment does not exist")
    
    approve_comment.is_approved = True
    approve_comment.is_read = True

    db.commit()
    db.refresh(approve_comment)

    return {
        "message": "Comment approved successfully",
        "comment": {
            "id": approve_comment.id,
            "name": approve_comment.name,
            "comment": approve_comment.comment
        }
    }

@comment_router.get("/approve")
async def approved_comments(db:dbDep, page: int =Query(1, ge=1), limit:int=Query(10, le=20)):

    skip = (page -1 ) * limit
    query = db.query(Comments).filter(Comments.is_approved == True)
    
    approved = query.order_by(Comments.created_at.desc()).offset(skip).limit(limit).all()

    total_approved = query.count()
    total_pages = (total_approved + limit -1) //limit

    return {
        "message": "Successfully fetched approved comments",
        "pagination": {
            "total": total_approved,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        },
        "approved_comments": approved,
        
    }


@comment_router.put("/read/{comment_id}")
async def mark_comment_as_read(comment_id: int, db: dbDep):
    comment = db.query(Comments).filter(Comments.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment.is_read = True
    db.commit()

    return {
        "message": "Comment marked as read",
        "comment_id": comment.id
    }

@comment_router.delete("/delete/{comment_id}")
async def delete_comment(comment_id: int, db: dbDep):
    comment = db.query(Comments).filter(Comments.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    db.delete(comment)
    db.commit()

    return {
        "message": "Comment deleted successfully",
        "deleted_id": comment_id
    }

