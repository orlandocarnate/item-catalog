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



# Create dummy user
User1 = User(name="Orlando Carnate", email="orlando.carnate@gmail.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()


# Create Entries
earrings = Category(user_id=1, name = 'Earrings')
# use session.add to add object myFirstCategory to staging zone before commit
session.add(earrings)
# commit to database
session.commit()

# ADD Earring item
earringItem = Jewelry(user_id=1, name = 'The Alyssa Earrings', 
                        price = '$11.99', 
                        category = earrings)

# add item
session.add(earringItem)

# commit to db
session.commit()

# Below are more categories
necklaces = Category(user_id=1, name = 'Necklaces')
session.add(necklaces)
session.commit()

bracelets = Category(user_id=1, name = 'Bracelets')
session.add(bracelets)
session.commit()

anklets = Category(user_id=1, name = 'Anklets')
session.add(anklets)
session.commit()



# EARRINGS
earringItem = Jewelry(user_id=1, name = 'Athena Earrings', 
                        price = '$11.99', 
                        category = earrings)
session.add(earringItem)
session.commit()

earringItem = Jewelry(user_id=1, name = 'Audrey Earrings', 
                        price = '$11.99', 
                        category = earrings)
session.add(earringItem)
session.commit()

# NECKLACES
necklaceItem = Jewelry(user_id=1, name = 'The Ella Necklace',
                        price = '$23.99',
                        category = necklaces)
session.add(necklaceItem)
session.commit()

necklaceItem = Jewelry(user_id=1, name = 'The Grace Necklace',
                        price = '$66.99', 
                        category = necklaces)
session.add(necklaceItem)
session.commit()

# Bracelets
braceletItem = Jewelry(user_id=1, name = 'The Alyssa Bracelet',
                        price = '$25.99', 
                        category = bracelets)
session.add(braceletItem)
session.commit()

braceletItem = Jewelry(user_id=1, name = 'The Amariah Bracelet',
                        price = '$34.99', 
                        category = bracelets)
session.add(braceletItem)
session.commit()

# Anklets
ankletItem = Jewelry(user_id=1, name = 'The Brittnet Anklet',
                        price = '$25.99', 
                        category = anklets)
session.add(ankletItem)
session.commit()

ankletItem = Jewelry(user_id=1, name = 'The Cameron Anklet',
                        price = '$24.99', 
                        category = anklets)
session.add(ankletItem)
session.commit()




# PYTHON COMMANDS - use this to QUERY ALL items in the database in Python
# >>> session.query(Category).all()