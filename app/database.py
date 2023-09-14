# Database Communication imports ---------
import psycopg2
from psycopg2.extras import RealDictCursor

# System Related imports -----------------
import os
import time
from dotenv import load_dotenv

# FastAPI modules ------------------------
from fastapi import HTTPException
from starlette.datastructures import Address

# Local files imports --------------------
from app.basemodel import Post
from app.basemodel import AddressDegree, PersonalInfo, Status

load_dotenv()


class DatabaseCredentials:
    def __init__(self, db_host, db_port, db_database, db_user, db_password):
        self.host = db_host
        self.port = db_port
        self.database = db_database
        self.user = db_user
        self.password = db_password


db_credentials = DatabaseCredentials(
    db_host=os.getenv("DB_HOST"),
    db_port=os.getenv("DB_PORT"),
    db_database=os.getenv("DB_DATABASE"),
    db_user=os.getenv("DB_USER"),
    db_password=os.getenv("DB_PASSWORD")
)

create_status_table_sql = """
CREATE TABLE IF NOT EXISTS statuses (
    id serial PRIMARY KEY,
    status VARCHAR(255) NOT NULL DEFAULT 'new'
);
"""

# Define the SQL statements to create tables
create_personal_info_table_sql = """
CREATE TABLE IF NOT EXISTS personal_info (
    id serial PRIMARY KEY,
    status_id INT REFERENCES statuses(id),  -- Reference to the status associated with this personal_info
    firstname VARCHAR(255),
    lastname VARCHAR(255),
    gender VARCHAR(255),
    birthdate VARCHAR(255),
    phone VARCHAR(255),
    email VARCHAR(255) UNIQUE
);
"""

create_address_degree_table_sql = """
CREATE TABLE IF NOT EXISTS address_degree (
    id serial PRIMARY KEY,
    personal_info_id INT REFERENCES personal_info(id),
    zipcode VARCHAR(255),
    stateProvince VARCHAR(255),
    townCity VARCHAR(255),
    degree VARCHAR(255),
    course VARCHAR(255),
    program VARCHAR(255),
    institution VARCHAR(255)
);
"""
while True:
    cursor = None
    connection = None
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

        if cursor:
            cursor.execute(create_status_table_sql)
            cursor.execute(create_personal_info_table_sql)
            cursor.execute(create_address_degree_table_sql)
            connection.commit()

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

    def create_post_personal_info(self, status_id, post: PersonalInfo):
        """ Creates new entries for personal_info table"""
        sql = """INSERT INTO personal_info (
                    status_id,
                    firstname,
                    lastname,
                    gender,
                    birthdate,
                    phone,
                    email
                    )
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING *"""
        try:
            self.cursor.execute(
                sql, (status_id, post.firstname, post.lastname, post.gender, post.birthdate, post.phone, post.email))
            new_personal_info_id = self.cursor.fetchone()[0]
            self.connection.commit()
            return new_personal_info_id
        except Exception as error:
            raise error

    def create_post_address_degree(self, personal_info_id, post: AddressDegree):
        """ Creates new entries for address_degree """
        sql = """INSERT INTO address_degree(
                    zipcode,
                    stateProvince,
                    townCity,
                    degree,
                    course,
                    program,
                    institution
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *"""
        try:
            self.cursor.execute(sql, (personal_info_id, post.zipcode, post.stateProvince,
                                post.townCity, post.degree, post.course, post.program, post.institution))
            self.connection.commit()
            return self.cursor.fetchall()
        except Exception as e:
            raise e

    def create_post_status(self, post: Status):
        """ Creates new entries for status"""
        sql = """INSERT INTO statuses (%s) VALUES (%s) RETURNING *"""

        try:
            self.cursor.execute(sql, (post.status,))
            self.connection.commit()
            return self.cursor.fetchone()[0]
        except Exception as e:
            raise e

    def create_entries(self, personal_info: PersonalInfo, address_degree: AddressDegree, status: Status):

        sql = """SELECT * FROM personal_info"""

        try:
            self.cursor.execute(sql)
            personal_info_data = self.cursor.fetchone()
        except Exception as e:
            raise e

        status_id = self.create_post_status(status)
        personal_info_id = self.create_post_personal_info(
            status_id, personal_info)
        address_degree_data = self.create_post_address_degree(
            personal_info_id, address_degree)

        return {"personal_info": personal_info_data, "address_degree": address_degree_data}

    def delete_post(self, target_id):
        """ Delete entries in the database with specified id """
        sql = """DELETE FROM personal_info WHERE id = %s RETURNING *"""
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
        sql = """SELECT * FROM personal_info WHERE id = %s"""
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
        sql = """SELECT * FROM personal_info"""
        try:
            self.cursor.execute(sql)
            posts = self.cursor.fetchall()
            return posts
        except Exception as error:
            raise error

    def update_post(self, target_id, post: PersonalInfo):
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
