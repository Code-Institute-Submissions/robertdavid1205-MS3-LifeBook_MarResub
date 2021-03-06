import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"): 
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)


# Code adapted after Code Institute's TravelTimN  -  Flask Rebuild 2020


@app.route("/")
@app.route("/get_books")
def get_books():
    books = list(mongo.db.books.find())
    return render_template("books.html", books=books)


@app.route("/search", methods=["GET", "POST"])
def search():
    # search a book
    query = request.form.get("query")
    books = list(mongo.db.books.find({"$text": {"$search": query}}))
    return render_template("books.html", books=books)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password is matching user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(request.form.get("username")))
                    return redirect(url_for(
                        "profile", username=session["user"]))
            else:
                # invalid password
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username does not exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # get the session username's user from database
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    return render_template("profile.html", username=username)

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    # add a new book
    if request.method == "POST":
        book = {
            "book_author": request.form.get("book_author"),
            "book_title": request.form.get("book_title"),
            "date_published": request.form.get("date_published"),
            "details": request.form.get("details"),
            "genre": request.form.get("genre"),
            "your_reason": request.form.get("your reason"),
            "created_by": session["user"]
        }
        mongo.db.books.insert_one(book)
        flash("Book Succesfully Added")
        return redirect(url_for("get_books"))

    return render_template("add_book.html")


@app.route("/edit_book/<book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    # edit added book
    if request.method == "POST":
        submit = {
            "book_author": request.form.get("book_author"),
            "book_title": request.form.get("book_title"),
            "date_published": request.form.get("date_published"),
            "details": request.form.get("details"),
            "genre": request.form.get("genre"),
            "your_reason": request.form.get("your reason"),
            "created_by": session["user"]
        }
        mongo.db.books.update({"_id": ObjectId(book_id)}, submit)
        flash("Book Succesfully Updated")

    book = mongo.db.books.find_one({"_id": ObjectId(book_id)})
    return render_template("edit_book.html", book=book)


@app.route("/delete_book/<book_id>")
# delete added book
def delete_book(book_id):
    mongo.db.books.remove({"_id": ObjectId(book_id)})
    flash("Book Successfully Deleted")
    return redirect(url_for("get_books"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)
