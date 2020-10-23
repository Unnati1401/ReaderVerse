from django.db import models
from django_neomodel import DjangoNode
from neomodel import StructuredNode, RelationshipTo, RelationshipFrom
from neomodel.properties import EmailProperty, DateProperty, StringProperty, FloatProperty, IntegerProperty
from neomodel.cardinality import OneOrMore, One, ZeroOrMore

class UserProfileInfo(DjangoNode):
    first_name = StringProperty(max_length=30,required = True)
    last_name = StringProperty(max_length=150, required = True)
    email = EmailProperty(unique=True,required = True)
    username = StringProperty(max_length=150, unique=True, required = True)
    password = StringProperty(max_length=10,unique=True, required = True)
    address = StringProperty(max_length=200)
    pincode = StringProperty(max_length=6)
    phone = StringProperty(max_length=10, required = True)
    favGenres = RelationshipTo('Genre','FAVORITEGENRE',cardinality=ZeroOrMore)
    favBook = RelationshipTo('Book','FAVORITEBOOK',cardinality=ZeroOrMore)
    bookExchange = RelationshipTo('BookExchange','BOOKEXCHANGE',cardinality=ZeroOrMore)
    bookDonate = RelationshipTo('BookDonate','BOOKDONATE',cardinality=ZeroOrMore)
    latitude = FloatProperty()
    longitude = FloatProperty()

    class Meta:
        app_label = 'core'
        
class BookExchange(DjangoNode):
    title = StringProperty()
    author = StringProperty()
    yearOfRelease = StringProperty()
    user = RelationshipFrom('UserProfileInfo','BOOKEXCHANGE',cardinality=One)

class BookDonate(DjangoNode):
    bookDonate = RelationshipFrom('Book','BOOKDONATE',cardinality=One)
    user = RelationshipFrom('UserProfileInfo','BOOKDONATE',cardinality=One)

class Book(DjangoNode):
    title = StringProperty() 
    image_url = StringProperty()
    yearOfRelease = StringProperty()
    rating = FloatProperty()
    user = RelationshipFrom('UserProfileInfo','FAVORITEBOOK',cardinality=ZeroOrMore)
    wrote = RelationshipFrom('Author','WROTE',cardinality=One)
    published = RelationshipFrom('Publisher','PUBLISHED',cardinality=One)
    genre = RelationshipFrom('Genre','GENRE',cardinality=OneOrMore)
    bookdonate = RelationshipTo('BookDonate','BOOKDONATE',cardinality=One)

class Author(DjangoNode):
    name = StringProperty()
    SEXES = {'F': 'Female', 'M': 'Male', 'O': 'Other'}
    sex = StringProperty(required=True, choices=SEXES)
    dob = StringProperty()
    numOfBooks = IntegerProperty()
    wrote = RelationshipTo('Book','WROTE',cardinality=ZeroOrMore)

class Publisher(DjangoNode):
    name = StringProperty()
    SEXES = {'F': 'Female', 'M': 'Male', 'O': 'Other'}
    sex = StringProperty(required=True, choices=SEXES)
    dob = StringProperty()
    numOfBooks = IntegerProperty()
    published = RelationshipTo('Publisher','Book',cardinality=OneOrMore)

class Genre(DjangoNode):
    name = StringProperty()
    bookGenre = RelationshipTo('Book','GENRE',cardinality=ZeroOrMore)
    favGenre = RelationshipFrom('UserProfileInfo','FAVORITEGENRE',cardinality=ZeroOrMore)
    
