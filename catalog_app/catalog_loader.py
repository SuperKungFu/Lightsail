from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, User, Category, Item

engine = create_engine('sqlite:///db/catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

user1 = User(name='Bret Peterson', email='kungfupeterson@gmail.com')
user2 = User(name='Fakey McFakerson', email='fakey@gmail.com')

category1 = Category(name="Star Wars")
category2 = Category(name="Legos")
category3 = Category(name="Marvel Super Heroes")

session.add(category1)
session.add(category2)
session.add(category3)
session.commit()

item1 = Item(name="Death Star",
             description="That's no moon...",
             category=category1, user=user1)
session.add(item1)
session.commit()

item2 = Item(name="Hoth",
             description="A stay at the Taun-Taun inn will rest you up.",
             category=category1, user=user1)
session.add(item2)
session.commit()

item3 = Item(name="Space Base",
             description="All of Benny's items",
             category=category2, user=user1)
session.add(item3)
session.commit()

item4 = Item(name="Spider Man",
             description="The web slinger keeps the city safe.",
             category=category3, user=user1)
session.add(item4)
session.commit()

item5 = Item(name="Iron Man",
             description="The suit makes the man.",
             category=category3, user=user2)
session.add(item5)
session.commit()
