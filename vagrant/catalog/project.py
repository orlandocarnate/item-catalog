# Insert imports here
from flask import Flask, render_template, request, redirect, url_for, flash, app, jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
import os

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
FB_ID = json.loads(open('fb_client_secret.json', 'r').read())['web']['app_id']
APPLICATION_NAME = "jewelry catalog"

app = Flask(__name__)

# DB connection
engine = create_engine('sqlite:///catalogwithusers.db', connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# make categories GLOBAL
categories = session.query(Category).all()

# Upload Global Variables
UPLOAD_FOLDER = 'static/upload'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png', 'gif'])


# ---------- app.routes here ----------

# HOME - All Categories Page
@app.route("/")
@app.route("/home")
def home():
    # If not logged in return PUBLIC page that shows LOGIN link
    if 'username' not in login_session:
        return render_template('shop/home.html', categories = categories)
    else:
        user_name = login_session['username']
        return render_template('shop/home.html', categories = categories, user_name = user_name)

# Login
@app.route("/login")
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
        for x in xrange(32))
    login_session['state'] = state
    # return "API key is " + apikey + "The current session state is %s" % login_session['state']
    return render_template('shop/login.html', STATE=state, apikey = CLIENT_ID, FB_apikey=FB_ID)

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

    login_session['provider'] = 'google'
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
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# FBCONNECT
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secret.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
        open('fb_client_secret.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]


    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output

# FBDISCONNECT
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

# DISCONNECT Google or Facebook
@app.route('/logoff')
def logoff():

    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('home'))
    else:
        flash("You were not logged in")
        return redirect(url_for('home'))


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



# list Categories in JSON format
@app.route('/JSON')
@app.route('/json')
def homeJSON():
    return jsonify(Category=[i.serialize for i in categories])

# list Category items in JSON format
@app.route('/<string:category_name>/JSON')
@app.route('/<string:category_name>/json')
def categoryJSON(category_name):
    category_name = category_name.title()
    category = session.query(Category).filter_by(name = category_name).one()
    items = session.query(Jewelry).filter_by(
        category_id=category.id).all()
    return jsonify(Jewelry=[i.serialize for i in items])

# list single item in JSON format
@app.route('/<string:category_name>/<int:item_id>/JSON')
@app.route('/<string:category_name>/<int:item_id>/json')
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
    if 'username' not in login_session:
        return render_template('shop/publiccategory.html', category = category, items = items, categories = categories)
    
    else:
        creator = getUserInfo(category.user_id)
        user_name = login_session['username']
        return render_template('shop/category.html', user_name = user_name, category = category, items = items, categories = categories, creator= creator)

# EDIT CATEGORY
@app.route("/<string:category_name>/edit/", methods=['GET','POST'])
def editCategoryPage(category_name):
    if 'username' not in login_session:
        return redirect('/login')
    editCategory = session.query(Category).filter_by(name = category_name).one()
    if request.method == 'POST':
        if request.form['name']:
            editCategory.name = request.form['name']
        if request.form['description']:
            editCategory.description = request.form['description']
        if request.form['category_image']:
            editCategory.category_image = request.form['category_image']
        session.add(editCategory)
        session.commit()
        flash('%s has been edited!' % editCategory.name)
        return redirect( url_for('categoryPage', category_name = category_name) )
    else:
        # user_name = login_session['username']
        category_images = os.listdir("static/img/categories/")
        return render_template('shop/editcategory.html', category_images = category_images, category = editCategory)


# VIEW Single Item - Single; Item Image
@app.route("/<string:category_name>/<int:item_id>/")
def itemPage(category_name, item_id):
    item = session.query(Jewelry).filter_by(id = item_id).one()
    category_id = item.category_id
    category = session.query(Category).filter_by(id = category_id).one()
    if 'username' not in login_session:
        return render_template('shop/publicitem.html', item = item, category = category)
    else:
        user_name = login_session['username']
        return render_template('shop/item.html', user_name = user_name,  item = item, category = category)

# NEW ITEM
@app.route("/<string:category_name>/new/", methods=['GET','POST'])
def newItem(category_name):
    category_name = category_name.title()
    current_category = session.query(Category).filter_by(name = category_name).one()
    if request.method == 'POST':
        new_category = session.query(Category).filter_by(name = request.form['category']).one()
        newJewelryItem = Jewelry(
                            name=request.form['name'], 
                            price=request.form['price'], 
                            description=request.form['description'], 
                            category_id = new_category.id, 
                            user_id=login_session['user_id']
                            )
        session.add(newJewelryItem)
        session.commit()
        flash('New Jewelry Item Created!')
        return redirect(url_for('categoryPage', category_name = category_name))
    else:
        user_name = login_session['username']
        return render_template('shop/newitem.html', current_category = current_category, categories=categories)

# EDIT Item - Add GET & POST Methods
@app.route("/<string:category_name>/<int:item_id>/edit", methods=['GET','POST'])
def editItem(category_name, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    editJewelryItem = session.query(Jewelry).filter_by(id = item_id).one()
    # Only Creator can edit.
    if editJewelryItem.user_id != login_session['user_id']:
        flash('Only the creator of this item can edit. You must create your own Jewelry item to edit.')
        return redirect(url_for('itemPage', category_name = category_name, item_id = item_id))
    
    if request.method == 'POST':
        if request.form['name']:
            editJewelryItem.name = request.form['name']
        if request.form['description']:
            editJewelryItem.description = request.form['description']
        if request.form['price']:
            editJewelryItem.price = request.form['price']
        if request.form['product_image']:
            editJewelryItem.product_image = request.form['product_image']
        session.add(editJewelryItem)
        session.commit()
        flash('%s has been edited!' % editJewelryItem.name)
        return redirect(url_for('itemPage', category_name = category_name, item_id = item_id))
    else:
        user_name = login_session['username']
        product_images = os.listdir("static/img/items/")
        return render_template('shop/edititem.html', user_name = user_name, category_name = category_name, item = editJewelryItem, product_images = product_images)

# DELETE ITEM
@app.route("/<string:category_name>/<int:item_id>/delete", methods=['GET','POST'])
def deleteItem(category_name, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    deleteItem = session.query(Jewelry).filter_by(id = item_id).one()
    if deleteItem.user_id != login_session['user_id']:
        flash('Only the creator of this item can delete this.')
        return redirect(url_for('itemPage', category_name = category_name, item_id = item_id))
    category_id = deleteItem.category_id
    category = session.query(Category).filter_by(id = category_id).one()
    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()
        flash('%s has been deleted!' % deleteItem.name)
        return redirect(url_for('categoryPage', category_name = category.name))
    else:
        user_name = login_session['username']
        return render_template('shop/deleteitem.html', user_name = user_name, category_name = category_name, item = deleteItem)

# UPLOAD IMAGE TEST PAGE
@app.route("/upload/")
def uploadImage():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
        return redirect(url_for('home'))
    else: 
        return render_template('upload.html')

# About Page
@app.route("/about")
def aboutPage():
    if 'username' not in login_session:
        return render_template('publicabout.html', categories = categories)
    else:
        user_name = login_session['username']
        return render_template('shop/about.html', user_name = user_name)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)