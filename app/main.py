from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI()


class Post(BaseModel):
    """ Data schame for post entities """
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


class PostManager:
    """ Post Managers class for handeling queries """

    def __init__(self) -> None:
        self.posts = []
        self.id = 0

    def create_post(self, post: Post):
        """ creates new post"""
        post_dict = post.dict()
        post_dict['id'] = self.id
        self.id += 1
        self.posts.append(post_dict)
        return post_dict

    def delete_post(self, target_id):
        """ deletes specific post with id """
        for post in self.posts:
            if target_id == post["id"]:
                self.posts.remove(post)
                return {"message": "post deleted successfully"}

            raise HTTPException(status_code=404, detail="Post not found")

    def get_post(self, target_id):
        """ gets specific post with id """
        for post in self.posts:
            if post['id'] == target_id:
                return post

            raise HTTPException(status_code=404, detail="Post not found")

    def get_all_posts(self):
        """ gets all post"""
        return self.posts


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


@app.get("/posts/{target_id}")
async def get_post(target_id: int):
    """
    Get a specific post by ID
    """
    return {"data": post_manager.get_post(target_id)}


@app.post("/posts")
async def create_post(data: Post):
    """
    Create a new post
    """
    return {"data": post_manager.create_post(data)}


@app.delete("/posts/{target_id}")
async def delete_post(target_id: int):
    """
    Delete a post by ID
    """
    return {"data": post_manager.delete_post(target_id)}
