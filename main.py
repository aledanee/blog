# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
import re

import Db_Operation
from classes import User, Login, BlogPost, Like, Comment, UsereRgi
from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import Optional
# import http
# from typing import FrozenSet, Optional

from fastapi import FastAPI, Path, Query
app: FastAPI = FastAPI()

#Enable CORS (Cross-Origin Resource Sharing)
origins = [
    "http://localhost:63342",   # Update this line with the correct port
    "http://localhost:8000",    # Assuming your frontend is served on this port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],  # You might want to restrict this to specific methods
    allow_headers=["*"],  # You might want to restrict this to specific headers
    expose_headers=["*"],
)

# Function to connect to MySQL
def connect_to_mysql():
    return Db_Operation.py.connect(host="localhost", user="root", password="morootok", db="blog")


@app.post("/register")
async def register_user(user_data: UsereRgi):
    conn = None
    try:
        conn = Db_Operation.connect_to_mysql("localhost", "root", "morootok", "blog")
        cursor = conn.cursor()

        # Extract user data from the request
        username = user_data.username
        email = user_data.email
        password = user_data.password
        profile_picture = user_data.profile_picture

        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return {"error": "Invalid email format."}

        # Check password length
        if len(password) < 8:
            return {"error": "Password must be at least 8 characters long."}

        # Check if user already exists
        query = f"SELECT * FROM User WHERE username='{username}' OR email='{email}'"
        cursor.execute(query)
        existing_user = cursor.fetchone()

        if not existing_user:
            # If user doesn't exist, create a new record
            query = f"INSERT INTO User (username, email, password, profile_picture) " \
                    f"VALUES ('{username}', '{email}', '{password}', '{profile_picture}')"
            cursor.execute(query)
            conn.commit()
            response = {"message": f"User '{username}' successfully registered"}
        else:
            response = {"error": "User already exists."}

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

    # Return the response
    return response


@app.post("/login")
async def login_user(user_data: Login, ):
    # Extract user information from the URL

    conn = Db_Operation.connect_to_mysql("localhost", "root", "morootok", "blog")

    # Extract user data from JSON
    username = user_data.username
    password = user_data.password

    # Check if user already exists
    cursor = conn.cursor()
    query = f"SELECT * FROM User WHERE username='{username}'"
    cursor.execute(query)
    existing_user = cursor.fetchone()

    # If user doesn't exist, create a new record
    if existing_user:
        if existing_user[3] == password:
            id_user = existing_user[0]
            response = {"id_user": id_user, "message": f"User '{id_user}' successfully login"}
        else:
            response = {"error": "username or password is incorrect1"}
    else:
        response = {"error": "username or password is incorrect2"}

    return response


@app.post("/create_new_post")
async def create_new_post(post_data: BlogPost):
    conn = Db_Operation.connect_to_mysql("localhost", "root", "morootok", "blog")
    cursor = conn.cursor()

    # Check if user already exists
    query = "SELECT * FROM User WHERE user_id=%s"
    cursor.execute(query, (post_data.author_id,))
    existing_user = cursor.fetchone()

    # If user doesn't exist, return an error
    if not existing_user:
        return {"error": "User not found."}

    # Insert the post without publication_date
    query = "INSERT INTO blogpost (title, content, author_id) VALUES (%s, %s, %s)"
    cursor.execute(query, (post_data.title, post_data.content, post_data.author_id))
    conn.commit()

    return {"message": f" '{post_data.title}' successfully posted"}


@app.post("/update_post")
async def update_post(post_data: BlogPost):
    conn = Db_Operation.connect_to_mysql("localhost", "root", "morootok", "blog")

    # Extract post data from JSON
    post_id = post_data.post_id
    title = post_data.title
    content = post_data.content
    publication_date = post_data.publication_date

    # Check if post already exists
    cursor = conn.cursor()
    query = f"SELECT * FROM blogpost WHERE post_id='{post_id}'"
    cursor.execute(query)
    existing_post = cursor.fetchone()

    # If post exists, update the existing post
    if existing_post:
        query = f"UPDATE blogpost SET title='{title}', content='{content}', publication_date='{publication_date}' WHERE post_id='{post_id}'"
        cursor.execute(query)
        conn.commit()
        response = {"message": f"Post '{post_id}' successfully updated"}
    else:
        # If post doesn't exist, return an error
        response = {"error": f"Post with id '{post_id}' not found"}

    return response


@app.get("/display_post")
async def display_post():
    conn = Db_Operation.connect_to_mysql("localhost", "root", "morootok", "blog")

    # Check if posts exist
    cursor = conn.cursor()
    query = "SELECT * FROM blogpost"
    cursor.execute(query)
    existing_posts = cursor.fetchall()

    # If posts exist, return the post details
    if existing_posts:
        posts_list = []
        for post in existing_posts:
            post_id = post[0]
            title = post[1]
            content = post[2]
            publication_date = post[3]

            post_details = {
                "post_id": post_id,
                "title": title,
                "content": content,
                "publication_date": publication_date
            }
            posts_list.append(post_details)

        response = {"posts": posts_list}
    else:
        response = {"error": "No posts found"}

    return response


@app.post("/like")
async def like(like_data: Like):
    conn = Db_Operation.connect_to_mysql("localhost", "root", "morootok", "blog")

    # Extract like data from JSON
    post_id = like_data.post_id
    user_id = like_data.user_id

    # Check if the post exists
    cursor = conn.cursor()
    query = f"SELECT * FROM BlogPost WHERE post_id='{post_id}'"
    cursor.execute(query)
    existing_post = cursor.fetchone()

    # If the post exists, proceed to like
    if existing_post:
        # Check if the user has already liked the post
        query = f"SELECT * FROM `Like` WHERE post_id='{post_id}' AND user_id='{user_id}'"
        cursor.execute(query)
        existing_like = cursor.fetchone()

        if existing_like:
            response = {"message": "User has already liked this post"}
        else:
            # Insert a new like record
            query = f"INSERT INTO `Like` (post_id, user_id) VALUES ('{post_id}', '{user_id}')"
            cursor.execute(query)
            conn.commit()
            response = {"message": "Post liked successfully"}
    else:
        raise HTTPException(status_code=404, detail="Post not found")

    return response


@app.post("/comment")
async def comment(comment_data: Comment):
    try:
        conn = Db_Operation.connect_to_mysql("localhost", "root", "morootok", "blog")
        cursor = conn.cursor()

        # Secure query using parameterized statements
        cursor.execute("SELECT * FROM BlogPost WHERE post_id=%s", (comment_data.post_id,))
        existing_post = cursor.fetchone()

        if existing_post:
            cursor.execute("INSERT INTO Comment (post_id, user_id, comment_text, comment_date) VALUES (%s, %s, %s, %s)",
                           (comment_data.post_id, comment_data.user_id, comment_data.comment_text, comment_data.comment_date))
            conn.commit()
            response = {"message": "Comment added successfully"}
        else:
            raise HTTPException(status_code=404, detail="Post not found")

    finally:
        conn.close()

    return response


@app.get("/like/count/{post_id}")
async def count_likes(post_id: int):
    conn = Db_Operation.connect_to_mysql("localhost", "root", "morootok", "blog")

    # Check if the post exists
    cursor = conn.cursor()
    query = f"SELECT * FROM BlogPost WHERE post_id='{post_id}'"
    cursor.execute(query)
    existing_post = cursor.fetchone()

    if existing_post:
        # Count the number of likes for the post
        query = f"SELECT COUNT(*) FROM `Like` WHERE post_id='{post_id}'"
        cursor.execute(query)
        like_count = cursor.fetchone()[0]

        response = {"post_id": post_id, "like_count": like_count}
    else:
        raise HTTPException(status_code=404, detail="Post not found")

    return response


@app.get("/comment/all/{post_id}")
async def get_all_comments(post_id: int):
    conn = Db_Operation.connect_to_mysql("localhost", "root", "morootok", "blog")

    # Check if the post exists
    cursor = conn.cursor()
    query = f"SELECT * FROM BlogPost WHERE post_id='{post_id}'"
    cursor.execute(query)
    existing_post = cursor.fetchone()

    if existing_post:
        # Retrieve all comments for the post
        query = f"SELECT * FROM Comment WHERE post_id='{post_id}'"
        cursor.execute(query)
        comments = cursor.fetchall()

        response = {"post_id": post_id, "comments": comments}
    else:
        raise HTTPException(status_code=404, detail="Post not found")

    return response


@app.get("/user")
async def read_user(username: str = Query(..., title="The username of the user to read")):
    conn = Db_Operation.connect_to_mysql("localhost", "root", "morootok", "blog")
    cursor = conn.cursor()

    # Fetch user data from the database based on username
    query = f"SELECT * FROM User WHERE username='{username}'"
    cursor.execute(query)
    user_data = cursor.fetchone()

    # If user does not exist, raise an HTTPException
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    # Create a User object using the retrieved data
    user = User(
        username=user_data[1],  # Assuming username is the second column in the User table
        email=user_data[2],     # Assuming email is the third column in the User table
        password=user_data[3],  # Assuming password is the fourth column in the User table
        profile_picture=user_data[4]  # Assuming profile_picture is the fifth column in the User table
    )

    return user


@app.get("/user", response_model=User)
async def read_user(username: str = Query(..., title="The username of the user to read")):
    conn = Db_Operation.connect_to_mysql("localhost", "root", "morootok", "blog")
    cursor = conn.cursor()

    # Fetch user data from the database based on username
    query = f"SELECT username, email, profile_picture FROM User WHERE username = %s"
    cursor.execute(query, (username,))
    user_data = cursor.fetchone()

    # Close the database connection
    cursor.close()
    conn.close()

    # If user does not exist, raise an HTTPException
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    # Create a User object using the retrieved data
    user = User(
        username=user_data[0],
        email=user_data[1],
        profile_picture=user_data[2]
    )

    return user

@app.get("/user/all")
async def get_all_users():
    conn = Db_Operation.connect_to_mysql("localhost", "root", "morootok", "blog")

    # Retrieve all users
    cursor = conn.cursor()
    query = "SELECT * FROM User"
    cursor.execute(query)
    users_data = cursor.fetchall()

    # If there are no users, return an empty list
    if not users_data:
        return {"users": []}

    # Convert each user data tuple to a User object
    users = [User(*user_data) for user_data in users_data]

    response = {"users": users}

    return response

@app.get("/display_post_for_more")
async def display_post():
    try:
        conn = Db_Operation.connect_to_mysql("localhost", "root", "morootok", "blog")

        # Retrieve posts with the most likes
        cursor = conn.cursor()
        query = """
        SELECT blogpost.*, COUNT(`Like`.post_id) AS like_count
        FROM blogpost
        LEFT JOIN `Like` ON blogpost.post_id = `Like`.post_id
        GROUP BY blogpost.post_id
        ORDER BY like_count DESC

        """
        cursor.execute(query)
        posts_with_likes = cursor.fetchall()

        # If posts with likes exist, return the post details
        if posts_with_likes:
            posts_list = []
            for post in posts_with_likes:
                post_id = post[0]
                title = post[1]
                content = post[2]
                publication_date = post[3]
                like_count = post[4]

                post_details = {
                    "post_id": post_id,
                    "title": title,
                    "content": content,
                    "publication_date": publication_date,
                    "like_count": like_count
                }
                posts_list.append(post_details)

            response = {"posts": posts_list}
        else:
            response = {"error": "No posts found"}

    except Exception as e:
        response = {"error": f"Internal Server Error: {str(e)}"}

    finally:
        if conn:
            conn.close()

    return response


@app.get("/post_titles")
async def get_post_titles():
    conn = Db_Operation.connect_to_mysql("localhost", "root", "morootok", "blog")

    # Retrieve post titles
    cursor = conn.cursor()
    query = "SELECT title FROM blogpost"
    cursor.execute(query)
    titles = [row[0] for row in cursor.fetchall()]

    if titles:
        response = {"post_titles": titles}
    else:
        raise HTTPException(status_code=404, detail="No posts found")

    return response

from fastapi import HTTPException

@app.get("/post_titles/{author_id}")
async def get_post_titles(author_id: int):
    conn = Db_Operation.connect_to_mysql("localhost", "root", "morootok", "blog")

    # Check if the author exists
    cursor = conn.cursor()
    query_check_author = f"SELECT * FROM User WHERE user_id='{author_id}'"
    cursor.execute(query_check_author)
    existing_author = cursor.fetchone()

    if existing_author:
        # Retrieve post titles for the author
        query = f"SELECT title FROM blogpost WHERE author_id='{author_id}'"
        cursor.execute(query)
        titles = [row[0] for row in cursor.fetchall()]

        if titles:
            response = {"author_id": author_id, "post_titles": titles}
        else:
            response = {"author_id": author_id, "message": "No posts found for the author"}
    else:
        raise HTTPException(status_code=404, detail=f"Author with ID {author_id} not found")

    return response

@app.delete("/delete_post/{post_id}")
async def delete_post(post_id: int):
    conn = Db_Operation.connect_to_mysql("localhost", "root", "morootok", "blog")

    # Check if the post exists
    cursor = conn.cursor()
    query_check = f"SELECT * FROM blogpost WHERE post_id='{post_id}'"
    cursor.execute(query_check)
    existing_post = cursor.fetchone()

    if existing_post:
        # Delete the post
        query_delete = f"DELETE FROM blogpost WHERE post_id='{post_id}'"
        cursor.execute(query_delete)
        conn.commit()
        response = {"message": f"Post with ID {post_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Post with ID {post_id} not found")

    return response
