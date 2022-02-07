import os

from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker 
import csv

from dotenv import load_dotenv
load_dotenv()

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

book=open("books.csv")
books = csv.reader(book)

for isbn,title,author,year in books:
    db.execute("INSERT INTO books (isbn, title, author, year) values(:isbn,:title,:author,:year)" ,{"isbn":isbn,"title":title,"author":author,"year":year})

db.commit()
