# Insert imports here
from flask import Flask, render_template, request, redirect, url_for, flash, app, jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

# OAUTH Imports
from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# Import columns from db_setup.py
from db_setup import Base, Category, Jewelry, User

# get client_id
# from apikeys import apikey
CLIENT_ID = json.loads(open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "jewelry catalog"

app = Flask(__name__)

# DB connection
engine = create_engine('sqlite:///catalogwithusers.db', connect_args={'check_same_thread': False})
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
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
        for x in xrange(32))
    login_session['state'] = state
    # return "API key is " + apikey + "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state, apikey = CLIENT_ID)

# GCONNECT
@app.route("/gconnect", methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # check if user exists, else make a new user.
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    #login_session.get('user_id') = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# GDISCONNECT - Revoke a current user's token ad reset login_session.
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response



# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None




# New Registration
@app.route("/register")
def register():
    return "<h1>Register Page<h1>"

# list Categories in JSON format
@app.route('/JSON')
def homeJSON():
    return jsonify(Category=[i.serialize for i in categories])

# list Category items in JSON format
@app.route('/<string:category_name>/JSON')
def categoryJSON(category_name):
    category_name = category_name.title()
    category = session.query(Category).filter_by(name = category_name).one()
    items = session.query(Jewelry).filter_by(
        category_id=category.id).all()
    return jsonify(Jewelry=[i.serialize for i in items])

# list single item in JSON format
@app.route('/<string:category_name>/<int:item_id>/JSON')
def itemJSON(category_name, item_id):
    item = session.query(Jewelry).filter_by(id = item_id).one()
    return jsonify(Jewelry=item.serialize)

# Single Category - All Items; Category Image
# list category items by category name
@app.route("/<string:category_name>/")
def categoryPage(category_name):
    category_name = category_name.title()
    category = session.query(Category).filter_by(name = category_name).one()
    items = session.query(Jewelry).filter_by(category = category)
    creator = getUserInfo(category.user_id)
    return render_template('category.html', category = category, items = items, categories = categories, creator= creator)


# NEW ITEM
@app.route("/<string:category_name>/new/", methods=['GET','POST'])
def newItem(category_name):
    if 'username' not in login_session:
        return redirect('/login')
    category_name = category_name.title()
    category = session.query(Category).filter_by(name = category_name).one()
    if request.method == 'POST':
        newJewelryItem = Jewelry(
                            name=request.form['name'], 
                            category_id = category.id, 
                            user_id=login_session['user_id']
                            )
        session.add(newJewelryItem)
        session.commit()
        flash('New Jewelry Item Created!')
        return redirect(url_for('categoryPage', category_name = category_name))
    else:
        return render_template('newitem.html', category = category)


# Single Item - Single; Item Image
@app.route("/<string:category_name>/<int:item_id>/")
def itemPage(category_name, item_id):
    item = session.query(Jewelry).filter_by(id = item_id).one()
    category_id = item.category_id
    category = session.query(Category).filter_by(id = category_id).one()
    return render_template('item.html', item = item, category = category)

# EDIT Item - Add GET & POST Methods
@app.route("/<string:category_name>/<int:item_id>/edit", methods=['GET','POST'])
def editItem(category_name, item_id):
    if 'username' not in login_session:
        return redirect('/login')
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
        flash('%s has been edited!' % editJewelryItem.name)
        return redirect(url_for('itemPage', category_name = category_name, item_id = item_id))
    else:
        return render_template('edititem.html', category_name = category_name, item = editJewelryItem)

# DELETE ITEM
@app.route("/<string:category_name>/<int:item_id>/delete", methods=['GET','POST'])
def deleteItem(category_name, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    deleteItem = session.query(Jewelry).filter_by(id = item_id).one()
    category_id = deleteItem.category_id
    category = session.query(Category).filter_by(id = category_id).one()
    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()
        flash('%s has been deleted!' % deleteItem.name)
        return redirect(url_for('categoryPage', category_name = category.name))
    else:
        return render_template('deleteitem.html', category_name = category_name, item = deleteItem)


# About Page
@app.route("/about")
def about():
    return "<h1>About Page<h1>"


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)