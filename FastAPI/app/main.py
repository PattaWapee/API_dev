from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor


app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

    

try:
    conn = psycopg2.connect(host = 'localhost', 
                            database = 'fastapi', 
                            user = 'postgres',
                            password= 'password123',
                            cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print("Connected to database")
except Exception as error:
    print("Error while connecting to database and error:", error)

class UpdatePost(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None
    rating: Optional[int] = None
    
my_posts = [{"title":"title1", "content":"content1", "id":1}, 
            {"title":"title2", "content":"content2", "id":2}]

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/posts")
def get_post():
    return {"data": my_posts}

@app.post("/post", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict= post.dict()
    post_dict['id'] = randrange(0, 1000000)
    my_posts.append(post_dict)
    return {"data": post_dict}

@app.get("/posts/latest")
def get_latest_post():
    return {"latest_post": my_posts[-1]}

def find_post(id):
    for post in my_posts:
        if post['id'] == id:
            return post
    return None
@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} not found")
    return {"post_detail": post}

@app.get("/posts/latest")
def get_latest_post():
    return {"latest_post": my_posts[-1]}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} not found")
    my_posts.remove(post)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}", status_code=status.HTTP_202_ACCEPTED)
def update_post(id: int, post: Post):
    post_dict = post.dict()
    post_dict['id'] = id
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} not found")
    my_posts.remove(post)
    my_posts.append(post_dict)
    return {"data": post_dict}