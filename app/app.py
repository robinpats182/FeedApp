from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends, status
from app.schema import PostCreate, UserCreate, UserRead, UserUpdate
from sqlalchemy import select, func
from app.db import Post, create_db_and_tables, get_async_session, User, Comment, Like
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy.orm import selectinload
from app.images import imagekit
import shutil
import os
import uuid
import tempfile
# from typing import Optional
from app.users import auth_backend, current_active_user, fastapi_users, get_user_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix='/auth/jwt', tags=["auth"])   
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(""),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        # Read file bytes
        file_bytes = await file.read()
        file.file.close()  # close the upload file
        
        upload_result = imagekit.files.upload(
            file=file_bytes,
            file_name=file.filename,
            use_unique_file_name=True,
            tags=["backend-upload"]
        )
        
        # Check if upload succeeded
        if upload_result and getattr(upload_result, "file_id", None):
            post = Post(
                user_id=user.id,
                username=user.username,
                caption=caption,
                url=upload_result.url,
                file_type="video" if file.content_type.startswith("video/") else "image",
                file_name=upload_result.name,
                imagekit_file_id=upload_result.file_id
            )
            
            session.add(post)
            await session.commit()
            await session.refresh(post)
            return post
        else:
            raise HTTPException(status_code=500, detail="ImageKit upload failed")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session),     
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = result.scalars().all()

    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "username": post.username,
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat(),
                # "username": post.user.username,
                # "email": post.user.email,
            }
        )
        
    return {"posts": posts_data}
    

@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user),):
    
    try:
        post_uuid = uuid.UUID(post_id)
        
        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="You don't have the permission to delete this post")
        
        imagekit.files.delete(post.imagekit_file_id)
        
        await session.delete(post)
        await session.commit()
        
        return {"sucess": True, "message": "Post deleted Sucessfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Custom endpoint: Allow users to delete their own account
@app.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    user: User = Depends(current_active_user),
    session = Depends(get_async_session),
):
    """Delete the current authenticated user's account."""
    try:
        await session.delete(user)
        await session.commit()
        return None
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/posts/{post_id}/like")
async def like_post(
    post_id: str,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        post_uuid = uuid.UUID(post_id)
        
        # Check if post exists
        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Check if user already liked this post
        like_result = await session.execute(
            select(Like).where(
                (Like.post_id == post_uuid) & (Like.user_id == user.id)
            )
        )
        existing_like = like_result.scalars().first()
        
        if existing_like:
            raise HTTPException(status_code=400, detail="You already liked this post")
        
        # Create like
        like = Like(post_id=post_uuid, user_id=user.id)
        session.add(like)
        await session.commit()
        
        return {"success": True, "message": "Post liked"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.delete("/posts/{post_id}/like")
async def unlike_post(
    post_id: str,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        post_uuid = uuid.UUID(post_id)
        
        # Find and delete the like
        result = await session.execute(
            select(Like).where(
                (Like.post_id == post_uuid) & (Like.user_id == user.id)
            )
        )
        like = result.scalars().first()
        
        if not like:
            raise HTTPException(status_code=404, detail="You haven't liked this post")
        
        await session.delete(like)
        await session.commit()
        
        return {"success": True, "message": "Post unliked"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/posts/{post_id}/likes")
async def get_likes_count(
    post_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        post_uuid = uuid.UUID(post_id)
        
        # Get likes count
        likes_result = await session.execute(
            select(func.count(Like.id)).where(Like.post_id == post_uuid)
        )
        likes_count = likes_result.scalar() or 0
        
        return {"likes_count": likes_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/posts/{post_id}/user-like")
async def check_user_liked(
    post_id: str,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        post_uuid = uuid.UUID(post_id)
        
        like_result = await session.execute(
            select(Like).where(
                (Like.post_id == post_uuid) & (Like.user_id == user.id)
            )
        )
        user_liked = like_result.scalars().first() is not None
        
        return {"user_liked": user_liked}
    except Exception as e:
        return {"user_liked": False}
    

@app.post("/posts/{post_id}/comment")
async def comment_post(
    post_id: str,
    content: str = Form(...),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        post_uuid = uuid.UUID(post_id)
        
        # Check if post exists
        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Create comment
        comment = Comment(
            post_id=post_uuid,
            user_id=user.id,
            username=user.username,
            content=content
        )
        session.add(comment)
        await session.commit()
        await session.refresh(comment)
        
        return {
            "id": str(comment.id),
            "username": comment.username,
            "content": comment.content,
            "created_at": comment.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/posts/{post_id}/comments")
async def get_post_comments(
    post_id: str,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        post_uuid = uuid.UUID(post_id)
        
        result = await session.execute(
            select(Comment).where(Comment.post_id == post_uuid).order_by(Comment.created_at.desc())
        )
        comments = result.scalars().all()
        await session.close()
        
        return {
            "comments": [
                {
                    "id": str(c.id),
                    "username": c.username,
                    "content": c.content,
                    "created_at": c.created_at.isoformat()
                }
                for c in comments
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: str,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        comment_uuid = uuid.UUID(comment_id)
        
        result = await session.execute(select(Comment).where(Comment.id == comment_uuid))
        comment = result.scalars().first()
        
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        if comment.user_id != user.id:
            raise HTTPException(status_code=403, detail="You can only delete your own comments")
        
        await session.delete(comment)
        await session.commit()
        
        return {"success": True, "message": "Comment deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))