import os
from fastapi import APIRouter, Depends, Form, HTTPException, status, File, UploadFile, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from shared.database.session import get_db
from shared.database.models import Post, User, MediaFile
from services.posts.app.models.schemas import (
    PostCreate, PostResponse, PostUpdate, PostFilter,
    CommentCreate, CommentResponse
)
from services.posts.app.services.post_service import PostService
from services.posts.app.services.media_service import MediaService
from services.auth.app.api.dependencies import get_current_active_user

router = APIRouter()

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    content: str = Form(...),
    location: str = Form(...),
    pet_id: int = Form(...),
    files: List[UploadFile] = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Crear la publicación en la base de datos
    new_post = Post(
        content=content, 
        location=location, 
        pet_id=pet_id,
        user_id=current_user.user_id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    # Ruta donde se guardarán los archivos
    media_directory = "media/"
    
    # Verificar si el directorio media/ existe, si no, crearlo
    if not os.path.exists(media_directory):
        os.makedirs(media_directory)
    
    # Manejar archivos adjuntos (si los hay)
    media_urls = []
    if files:
        for file in files:
            file_location = f"{media_directory}{file.filename}"
            try:
                with open(file_location, "wb") as buffer:
                    buffer.write(file.file.read())

                
                new_media = MediaFile(
                    post_id=new_post.post_id, 
                    media_url=file_location,
                    user_id=current_user.user_id,  # Añadido
                    media_type=file.content_type   # Añadido
                )
                db.add(new_media)
                db.commit()
                media_urls.append(file_location)
            except Exception as e:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error guardando el archivo {file.filename}: {str(e)}"
                )

    return {
        "content": new_post.content,
        "location": new_post.location,
        "pet_id": new_post.pet_id,
        "post_id": new_post.post_id,
        "user_id": new_post.user_id,
        "created_at": new_post.created_at,
        "updated_at": new_post.updated_at,
        "media_urls": media_urls,
        "comments_count": 0,
        "reactions_count": 0,
        "comments": []
    }

@router.get("/", response_model=List[PostResponse])
async def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    pet_id: Optional[int] = None,
    location: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    has_media: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Get all posts with optional filters
    """
    filters = PostFilter(
        pet_id=pet_id,
        location=location,
        from_date=from_date,
        to_date=to_date,
        has_media=has_media
    )
    return await PostService.get_posts(db, skip, limit, filters)

@router.get("/my-posts", response_model=List[PostResponse])
async def get_my_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all posts from the current user
    """
    filters = PostFilter(user_id=current_user.user_id)
    return await PostService.get_posts(db, skip, limit, filters)

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific post by ID
    """
    return await PostService.get_post(db, post_id)

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a post
    """
    return await PostService.update_post(db, current_user.user_id, post_id, post_data)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a post
    """
    await PostService.delete_post(db, current_user.user_id, post_id)
    return {"status": "success"}

@router.post("/{post_id}/media", response_model=PostResponse)
async def add_media_to_post(
    post_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add media to an existing post
    """
    post = await PostService.get_post(db, post_id)
    if post.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this post"
        )
    
    media_url = await MediaService.save_media(file, post_id)
    post.media_urls.append(media_url)
    db.commit()
    
    return post