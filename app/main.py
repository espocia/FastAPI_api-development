#  Local files imports --------------------
from app.database import PostManager
from app.basemodel import AddressDegree, PersonalInfo, Post, Status

# FastAPI import -------------------------
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="GUTZ online application services  API")

origins = [
    "http://localhost:5173",  # Replace with your React app's URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # You can specify specific HTTP methods if needed
    allow_headers=["*"],  # You can specify specific HTTP headers if needed
)

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
async def create_post(personal_info: PersonalInfo, address_degree: AddressDegree, status: Status):
    """
    Create a new post
    """
    status_id = post_manager.create_post_status(status)
    personal_info_id = post_manager.create_post_personal_info(
        status_id, personal_info)
    return {"data": post_manager.create_post_address_degree(personal_info_id, address_degree)}


@app.put("/post/{target_id}")
async def update_post(target_id: int, status: Status):
    """
    Update existing post
    """
    return {"data": post_manager.update_status(target_id, status)}


@app.delete("/post/{target_id}")
async def delete_post(target_id: int):
    """
    Delete a post by ID
    """
    return {"data": post_manager.delete_post(target_id)}
