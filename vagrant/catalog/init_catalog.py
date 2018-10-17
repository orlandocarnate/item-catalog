# Create sample items in the catalog database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#Import classes from 'db_setup.py'
from db_setup import Base, Category, Jewelry

# Lets program know which database to use
engine = create_engine('sqlite:///catalog.db')

# Bind engine with Base class - connects class definintions with
# their corresponding tables in the database
Base.metadata.bind = engine

# establish a link of communication between code executions and the engine
DBSession = sessionmaker(bind = engine)

# Sessions are used for CRUD functions before being committed
session = DBSession()

# Create Entries
earrings = Category(name = 'Earrings')
# use session.add to add object myFirstCategory to staging zone before commit
session.add(category1)

# commit to database
session.commit()

# ADD Jewelry item
earringItem = Jewelry(name = 'The Alyssa Earrings', 
                        description = '', 
                        price = '$11.99', 
                        category = earrings)

# add item
session.add(jewelryItem1)

# commit to db
session.commit()

# Below are more categories
necklaces = Category(name = 'Necklaces')
session.add(nacklaces)
session.commit()

bracelets = Category(name = 'Bracelets')
session.add(bracelets)
session.commit()

anklets = Category(name = 'Anklets')
session.add(anklets)
session.commit()



# EARRINGS
earringItem = Jewelry(name = 'Athena Earrings', 
                        description = '', 
                        price = '$11.99', 
                        category = earrings)
session.add(earringItem)
session.commit()

earringItem = Jewelry(name = 'Audrey Earrings', 
                        description = '', 
                        price = '$11.99', 
                        category = earrings)
session.add(earringItem)
session.commit()

# NECKLACES
necklaceItem = Jewelry(name = 'The Gina Necklace', 
                        description = '', 
                        price = '$23.99', 
                        category = necklaces)
session.add(necklaceItem)
session.commit()

necklaceItem = Jewelry(name = 'The Grace Necklace', 
                        description = '', 
                        price = '$66.99', 
                        category = necklaces)
session.add(necklaceItem)
session.commit()






# PYTHON COMMANDS - use this to QUERY ALL items in the database in Python
# >>> session.query(Category).all()