#  Local files imports --------------------
from app.database import PostManager
from app.basemodel import AddressDegree, PersonalInfo,  Status, File

# FastAPI import -------------------------
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

# feature --------------------------------
from app.mailer import confim_application
from botocore.exceptions import NoCredentialsError
import boto3
import os

app = FastAPI(title="GUTZ online application services  API")

post_manager = PostManager()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    # Specify the origin(s) you want to allow
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # You can specify the allowed HTTP methods
    allow_headers=["*"],  # You can specify the allowed headers
)

# Add a middleware to handle mixed content

AWS_ACCESS_KEY_ID = os.environ.get("ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = os.environ.get("BUCKET_NAME")
AWS_DIR = "resume/"


s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)


@app.get("/")
async def root():
    """
    Welcome endpoint
    """
    return {"message": "Welcome to my API"}


@app.post("/uploadfile/")
async def upload_file(file: UploadFile):
    try:
        # Upload file to S3 bucket
        object_key = AWS_DIR + file.filename
        s3.upload_fileobj(
            file.file,
            AWS_BUCKET_NAME,
            object_key
        )
        return JSONResponse(content={"message": "File uploaded successfully"}, status_code=200)
    except NoCredentialsError:
        return JSONResponse(content={"error": "AWS credentials not found"}, status_code=500)


@app.get("/downloadfile/{file_name}")
async def download_file(file_name: str):
    try:
        # Download file from S3 bucket to the server's local filesystem
        # Provide the local path where you want to save the file
        object_key = AWS_DIR + file_name
        local_file_path = f"/tmp/{file_name}"  # Use a temporary directory
        s3.download_file(
            AWS_BUCKET_NAME,
            object_key,
            local_file_path
        )

        # Serve the downloaded file as a response for download
        return FileResponse(
            local_file_path,
            headers={
                "Content-Disposition": f"attachment; filename={file_name}"
            }
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


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
async def create_post(personal_info: PersonalInfo, address_degree: AddressDegree, status: Status, file: File):
    """
    Create a new post
    """
    try:
        file_id = post_manager.create_post_file(file)
        status_id = post_manager.create_post_status(status)
        personal_info_id = post_manager.create_post_personal_info(
            status_id, file_id, personal_info)
        post_manager.create_post_address_degree(
            personal_info_id, address_degree)
        confim_application(personal_info.email, personal_info.firstname)
        return {"message": "submitted succesfully"}
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


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
