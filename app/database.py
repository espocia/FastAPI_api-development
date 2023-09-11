from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time


app = FastAPI()


class Post(BaseModel):
    """ Data schame for post entities """
    title: str
    content: str
    published: bool = True


class DatabaseCredentials:
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password


db_credentials = DatabaseCredentials(
    host="my-postgres-db.cdnlaegejvgw.us-east-1.rds.amazonaws.com",
    port=5432,
    database="fastapi",
    user="postgres",
    password="josh2000"  # Replace with your actual password
)

while True:
    try:
        connection = psycopg2.connect(
            host=db_credentials.host,
            database=db_credentials.database,
            user=db_credentials.user,
            password=db_credentials.password,
            cursor_factory=RealDictCursor
        )
        cursor = connection.cursor()
        print('Database connection was successfully')
        break
    except Exception as e:
        print('Connecting to database failed')
        print(e)
        time.sleep(2)


class PostManager:
    """ Post Managers class for handeling queries """

    def __init__(self) -> None:
        self.connection = connection
        self.cursor = cursor

    def create_post(self, post: Post):
        """ Creates new entries for the database """
        sql = """INSERT INTO posts (title, content, published) VALUES (%s,%s,%s) RETURNING *"""
        try:
            self.cursor.execute(
                sql, (post.title, post.content, post.published))
            new_post = self.cursor.fetchone()
            self.connection.commit()
            return new_post
        except Exception as error:
            raise error

    def delete_post(self, target_id):
        """ Delete entries in the database with specified id """
        sql = """DELETE FROM posts WHERE id = %s RETURNING *"""
        try:
            self.cursor.execute(sql, (target_id,))
            deleted_post = self.cursor.fetchone()
            if deleted_post is None:
                raise HTTPException(status_code=404, detail="Post not found")
            return deleted_post
        except Exception as error:
            raise error

    def get_post(self, target_id):
        """ Gets specific postt in the database with specified id """
        sql = """SELECT * FROM posts WHERE id = %s"""
        try:
            self.cursor.execute(sql, (target_id,))
            post = self.cursor.fetchone()
            if post is None:
                raise HTTPException(status_code=404, detail="Post not found")
            return post
        except Exception as error:
            raise error

    def get_all_posts(self):
        """ Get all post in the database"""
        sql = """SELECT * FROM posts"""
        try:
            self.cursor.execute(sql)
            posts = self.cursor.fetchall()
            return posts
        except Exception as error:
            raise error

    def update_post(self, target_id, post: Post):
        """ Update exisiting post with specified id and schema"""
        try:
            get_post_sql = """SELECT id FROM posts WHERE id = %s"""
            self.cursor.execute(get_post_sql, (target_id,))
            existing_post = self.cursor.fetchone()
            if existing_post:
                update_sql = """UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *"""
                self.cursor.execute(
                    update_sql, (post.title, post.content, post.published, target_id))
                updated_post = self.cursor.fetchone()
                self.connection.commit()
                return updated_post
            raise HTTPException(status_code=404, detail="Post not found")
        except Exception as error:
            raise error


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
async def create_post(data: Post):
    """
    Create a new post
    """
    return {"data": post_manager.create_post(data)}


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
