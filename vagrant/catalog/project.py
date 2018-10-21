# Insert imports here
from flask import Flask, render_template, request, redirect, url_for, flash, app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import columns from db_setup.py
from db_setup import Base, User, Category, Jewelry


app = Flask(__name__)

# DB connection
engine = create_engine('sqlite:///catalog.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# app.routes here

# HOME - All Categories Page
@app.route("/")
@app.route("/home")
def home():
    categories = session.query(Category).all()
    return render_template('home.html', categories = categories)

# Login
@app.route("/login")
def login():
    return "<h1>Login Page<h1>"

# New Registration
@app.route("/register")
def register():
    return "<h1>Register Page<h1>"

# Single Category - All Items; Category Image
# list category items by category name
@app.route("/<string:category_name>/")
def categoryPage(category_name):
    category = session.query(Category).filter_by(name = category_name).one()
    items = session.query(Jewelry).filter_by(category = category)

    return render_template('category.html', category = category.name, items = items)

    #output = "<h1>" + category1.name + "</h1>"
    #return output

# Single Item - Single; Item Image
@app.route("/<int:item_id>/")
def itemPage(item_id):
    item = session.query(Jewelry).filter_by(id = item_id).one()
    output = "<h1>" + item.name + "</h1>"
    return output

'''
# New Category - Default Image or Upload Image
@app.route("/newcategory")
def newCategory():
    return "<h1>New Category Page<h1>"




# New Product - Default Image or Upload Image
@app.route("/<string:category_name>/new", methods=['GET','POST'])
def newProduct(category_name):
    category = session.query(Category).filter_by(name = category_name).one()
    if request.method == 'POST':
        # category_id is the linked foreign key for jewelry table
        newItem = Jewelry(name = request.form['name'], price = request.form['price'], description = request.form['description'], category_id = category_id) 
        # stage the newItem variable before committing to DB using session.add
        session.add(newItem)
        # commit to DB
        session.commit()
        # run the categoryPage() to return to the category's main page        
        return redirect(url_for('categoryPage', category_name = category_name))
    else:
        return render_template('newitem.html', category_name = category_name, items = items)
'''

# About Page
@app.route("/about")
def about():
    return "<h1>About Page<h1>"

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)