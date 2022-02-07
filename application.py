import os
from re import search

from flask import Flask, session, request, render_template, redirect, flash
import flask
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required 
import requests


app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = '12345'

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@login_required
def index():
    return redirect("/search")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username")
            print("must provide username")
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password")
            print("must provide password")
            return redirect("/login")

        # Query database for username
        rows = db.execute("SELECT * FROM usuarios WHERE username = :username",
                         { "username":request.form.get("username")}).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["pass"], request.form.get("password")):
            flash('invalid username and/or password')
            print("invalid username and/or password")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        return redirect("/")

        # Redirect user to home page

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")

    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
           flash("must provide username")
           print("must provide username")
           return redirect("/register")

        if not password:
            flash("must provide password")
            print("must provide password")
            return redirect("/register")
        if not confirmation:
            flash("must provide password confirmation")
            return redirect("/register")

        usernames = []
        exist = db.execute("SELECT username FROM usuarios WHERE username=:username",{
            "username":username 
        }).fetchone()
        if exist:
            flash("username already exist")
            return redirect("/register")

        if password != confirmation:
            flash("check password confirmation")
            return redirect("/register")

        db.execute("INSERT INTO usuarios (username, pass) VALUES (:username, :password)",
                   {"username":username, "password":generate_password_hash(password)})
        db.commit()
        flash("already register, please login")
        return redirect("/login")

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method=="POST":
        search = "%"+ request.form.get("search").upper() + "%"
        rows = db.execute("SELECT * FROM books WHERE UPPER(isbn) LIKE :search OR UPPER(title) LIKE :search or UPPER(author) LIKE :search  or year LIKE :search limit 20",
                         { "search": search}).fetchall()
        
        return render_template("search.html",resultados=rows)
    else:
        return render_template("search.html")


@app.route("/book/<isbn>", methods=["GET", "POST"])
@login_required
def book(isbn):
    if request.method=="POST":

        comment = request.form.get("comment")
        rating = request.form.get("rating")

        db.execute("INSERT INTO reseñas (id_book, id_usuario, comentarios, puntaje) VALUES (:id_book, :id_usuario, :comentarios, :puntaje)",
                   {"id_book":isbn, "id_usuario": session["user_id"], "comentarios":comment, "puntaje":rating })
        db.commit()
        flash("Comment done!")
        return redirect("/book/"+isbn)

    else:
        book = db.execute("SELECT * FROM books WHERE isbn=:isbn",
                         { "isbn": isbn}).fetchone()
        if not book:
            flash("isbn invalid")
            return redirect("/search")

        reseña = db.execute("SELECT * FROM reseñas WHERE id_book= :isbn",
                         { "isbn": isbn}).fetchall()

        
        ifopined  = db.execute("SELECT * FROM reseñas WHERE id_book= :isbn AND id_usuario=:id_usuario",
                         { "isbn": isbn, "id_usuario": session["user_id"]}).fetchone()
        response = requests.get("https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbn).json()
        print(response)

        try:
            descripcion = response["items"][0]["volumeInfo"]["description"]
        except KeyError:
            descripcion= "not available content"   
        try:
            average_rating = response["items"][0]["volumeInfo"]["averageRating"]
        except KeyError:
            average_rating= "not available content"   
        try:
            ratings_count = response["items"][0]["volumeInfo"]["ratingsCount"]
        except KeyError:
            ratings_count= "not available content"   
        try:
            image = response["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]
        except KeyError:
            image= "https://png.pngtree.com/png-vector/20210215/ourlarge/pngtree-template-internet-banner-with-glitch-effect-error-page-pixel-graphic-crash-png-image_2910993.jpg"   
        book_data= {
            "title":book[1],
            "author":book[2],
            "year":book[3],
            "description": descripcion,
            "average_rating": average_rating,
            "rating_count":ratings_count,
            "image":image,
        }

        return render_template("book.html", book_data=book_data, reviews=reseña, ifopined=ifopined)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

        