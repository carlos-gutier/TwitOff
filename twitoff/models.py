"""SQLAlchemy models for TwitOff."""
from flask_sqlalchemy import SQLAlchemy

DB = SQLAlchemy()

# A model is just a class (this is a User class)
# and inherits/it's a subclass of the DB.Model class
class User(DB.Model):
    """Twitter users that we pull and analyze Tweets for."""
    id = DB.Column(DB.Integer, primary_key =True)
    name = DB.Column(DB.String(15), nullable=False)

class Tweet(DB.Moder):
    id = DB.Column(DB.Integer, primary_key=True)
    text = DB.Column(DB.Unicode(280))
