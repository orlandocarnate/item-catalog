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

# make categories GLOBAL
categories = session.query(Category).all()

# app.routes here

# HOME - All Categories Page
@app.route("/")
@app.route("/home")
def home():

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
    category_name = category_name.title()
    category = session.query(Category).filter_by(name = category_name).one()
    items = session.query(Jewelry).filter_by(category = category)

    return render_template('category.html', category = category, items = items, categories = categories)


# NEW ITEM
@app.route("/<string:category_name>/new/", methods=['GET','POST'])
def newItem(category_name):
    category_name = category_name.title()
    category = session.query(Category).filter_by(name = category_name).one()
    if request.method == 'POST':
        newJewelryItem = Jewelry(name=request.form['name'], category_id = category.id)
        session.add(newJewelryItem)
        session.commit()
        flash('New Jewelry Item Created!')
        return redirect(url_for('categoryPage', category_name = category_name))
    else:
        return render_template('newitem.html', category = category)


# Single Item - Single; Item Image
@app.route("/<int:item_id>/")
def itemPage(item_id):
    item = session.query(Jewelry).filter_by(id = item_id).one()
    category_id = item.category_id
    category = session.query(Category).filter_by(id = category_id).one()
    return render_template('item.html', item = item, category_name = category.name)

# EDIT Item - Add GET & POST Methods
@app.route("/<int:item_id>/edit", methods=['GET','POST'])
def editItem(item_id):
    editJewelryItem = session.query(Jewelry).filter_by(id = item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editJewelryItem.name = request.form['name']
        if request.form['description']:
            editJewelryItem.description = request.form['description']
        if request.form['price']:
            editJewelryItem.price = request.form['price']
        session.add(editJewelryItem)
        session.commit()
        flash('Item has been edited!')
        return redirect(url_for('itemPage', item_id = item_id))
    else:
        return render_template('edititem.html', item = editJewelryItem)

# DELETE ITEM
@app.route("/<int:item_id>/delete", methods=['GET','POST'])
def deleteItem(item_id):
    deleteItem = session.query(Jewelry).filter_by(id = item_id).one()
    category_id = deleteItem.category_id
    category = session.query(Category).filter_by(id = category_id).one()
    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()
        flash('Item has been deleted!')
        return redirect(url_for('categoryPage', category_name = category.name))
    else:
        return render_template('deleteitem.html', item = deleteItem)


# About Page
@app.route("/about")
def about():
    return "<h1>About Page<h1>"

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)