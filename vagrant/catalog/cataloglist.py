# Create sample items in the catalog database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#Import classes from 'db_setup.py'
from db_setup import Base, Category, Jewelry, User

# Lets program know which database to use
engine = create_engine('sqlite:///catalogwithusers.db')

# Bind engine with Base class - connects class definintions with
# their corresponding tables in the database
Base.metadata.bind = engine

# establish a link of communication between code executions and the engine
DBSession = sessionmaker(bind = engine)

# Sessions are used for CRUD functions before being committed
session = DBSession()

# List Categories
def category_list():
    categories = session.query(Category).all()
    for category in categories:
        print('Category: {0} ID: {1} Image {2}'.format(category.name, category.id, category.category_image))
    return

# List Items
def item_list():
    items = session.query(Jewelry).all()
    for item in items:
        print('Item: {0} ID: {1} Price: {2} Category ID: {3} Image: {4}'.format(item.name, item.id, item.price, item.category_id, item.product_image))
    return

# List Users
def user_list():
    users = session.query(User).all()
    for user in users:
        print('User: {0} ID: {1} Email {2}'.format(user.name, user.id, user.email))
    return

print('CATEGORIES')
category_list()
print('ITEMS')
item_list()
print('Users')
user_list()