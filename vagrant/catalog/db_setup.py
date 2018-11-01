### CONFIGURATION ###
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
# for configuration and class code
from sqlalchemy.ext.declarative import declarative_base
# import to create Foreign Key relationship
from sqlalchemy.orm import relationship
# used for configuratiion code at end of file
from sqlalchemy import create_engine

# instance of delcarative Base class to let SQLAlchemy know that our classes are special classes to create tables
Base = declarative_base()

### CLASS CODE ###
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False)
    picture = Column(String(250))

class Category(Base):
    # Assign TABLE Name
    __tablename__ = 'category'

    # MAPPER CODE - define columns for category table
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    category_image = Column(String(80), nullable=False, default="700x400.png")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    
    # JSON Configuration
    @property
    def serialize(self):

        return {
            'id': self.id,
            'name': self.name,
        }

class Jewelry(Base):
    # Assign TABLE name
    __tablename__ = 'jewelry'

    # MAPPER CODE - create columns for jewelry
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    status = Column(String(80)) # New item, on sale, etc
    price = Column(String(8))
    product_image = Column(String(80), nullable=False, default="default.jpg")

    # specify FOREIGN KEY ID
    category_id = Column(Integer, ForeignKey('category.id'))

    #Establish relationship with other table
    category = relationship(Category)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # JSON Configuration
    @property
    def serialize(self):

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
        }


### Ending CONFIGURATION ###

# create an engine that stores data in the local
# directory's 'catalog.db' file
engine = create_engine('sqlite:///catalogwithusers.db')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)