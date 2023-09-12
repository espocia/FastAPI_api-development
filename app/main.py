#  Local files imports --------------------
from app.database import PostManager
from app.basemodel import PersonalInfo, Post

# FastAPI import -------------------------
from fastapi import FastAPI

app = FastAPI(title="GUTZ online application services  API")

post_manager = PostManager()


@app.get("/")
async def root():
    """
    Welcome endpoint
    """
    return {"message": "Welcome to my API"}


@app.get("/posts")
async def get_posts():
    """
    Get all posts
    """
    return {"data": post_manager.get_all_posts()}


@app.get("/post/{target_id}")
async def get_post(target_id: int):
    """
    Get a specific post by ID
    """
    return {"data": post_manager.get_post(target_id)}


@app.post("/post")
async def create_post(data: PersonalInfo):
    """
    Create a new post
    """
    return {"data": post_manager.create_post_personal_info(data)}


@app.put("/post/{target_id}")
async def update_post(target_id: int, data: Post):
    """
    Update existing post
    """
    return {"data": post_manager.update_post(target_id, data)}


@app.delete("/post/{target_id}")
async def delete_post(target_id: int):
    """
    Delete a post by ID
    """
    return {"data": post_manager.delete_post(target_id)}
