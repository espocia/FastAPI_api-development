#  Local files imports --------------------
from app.database import PostManager
from app.basemodel import AddressDegree, PersonalInfo,  Status

# FastAPI import -------------------------
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="GUTZ online application services  API")

post_manager = PostManager()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    # Specify the origin(s) you want to allow
    allow_origins=["https://dulcet-melba-efe48a.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],  # You can specify the allowed HTTP methods
    allow_headers=["*"],  # You can specify the allowed headers
)

# Add a middleware to handle mixed content


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
