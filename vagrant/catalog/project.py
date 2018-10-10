# Insert imports here
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, url_for, flash, redirect, app

app = Flask(__name__)

# DB connection

# Sample Dictionary for DB
categories = [
    {
        'category_id': '1',
        'category_name': 'Necklaces',
        'picture': 'necklaces.jpg',
        'description': 'For the neck',
    },
    {
        'category_id': '2'
        'category_name': 'Earrings',
        'picture': 'earrings.jpg',
        'description': 'For the earlobes',
    }
]

products = [
    {
        'product_id': '1',
        'category_id': '1',
        'picture': 'necklace1.jpg',
        'description': 'Necklace product 1',
        'date_posted': 'April 20, 2018'
    },
    {
        'product_id': '2',
        'category_id': '1',
        'picture': 'necklace1.jpg',
        'description': 'Necklace product 2',
        'date_posted': 'April 20, 2018'
    }
]

# app.routes here

# HOME - All Categories Page
@app.route("/")
@app.route("/home")
def home():
    # return "<h1>Home Page<h1>"
    #return render_template('home.html', categories=categories)
    return render_template('home.html')

# Login
@app.route("/login")
def login():
    return "<h1>Login Page<h1>"

# New Registration
@app.route("/register")
def register():
    return "<h1>Register Page<h1>"

# Single Category - All Items; Category Image
#@app.route("/category/<int:category_id>/")
#def register():
#    return "<h1>Category Page<h1>"

# New Category - Default Image or Upload Image
@app.route("/newcategory")
def newCategory():
    return "<h1>New Category Page<h1>"

# Product - Edit or Delete
#@app.route("/category/<int:category_id>/<int:product_id>")
#def product():
#    return "<h1>Product Page<h1>"


# New Product - Default Image or Upload Image
#@app.route("/category/<int:category_id>/new_product")
#def newProduct()):
    return "<h1>New Product Page<h1>"


# About Page
@app.route("/about")
def about():
    return "<h1>About Page<h1>"

if __name__ == '__main__':
    # app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)