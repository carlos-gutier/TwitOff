"""Retrieve Tweets, embeddings, and persist in the database."""
import basilica
import tweepy
from decouple import config
from .models import DB, Tweet, User

TWITTER_AUTH = tweepy.OAuthHandler(config('TWITTER_CONSUMER_KEY'),
                                   config('TWITTER_CONSUMER_SECRET'))
TWITTER_AUTH.set_access_token(config('TWITTER_ACCESS_TOKEN'),
                              config('TWITTER_ACCESS_TOKEN_SECRET'))
TWITTER = tweepy.API(TWITTER_AUTH)

BASILICA = basilica.Connection(config('BASILICA_KEY'))


def add_or_update_user(username):
    """Add or update a user *and* their Tweets, error if no/private user."""
    try:
        twitter_user = TWITTER.get_user(username)
        # Using logic statement below trying to get user from DB first
        # in case it already exist -- to add or update -- if it already
        # exists then it returns None (Falser)
        # then it would evaluate (with 'or') to the second term
        # a new user object with id and name
        db_user = (User.query.get(twitter_user.id) or
                   User(id=twitter_user.id, name=username))
        DB.session.add(db_user) # we add to DB without commiting yet
        
        # We want as many recent non-retweet/reply statuses as we can get
        # if since_id=None, then it gets the most recent tweets it can
        tweets = twitter_user.timeline(
            count=200, exclude_replies=True, include_rts=False,
            tweet_mode='extended', since_id=db_user.newest_tweet_id)
        
        if tweets: # only if the user has tweets
            # now that we have the DB user we want to update
            # the newest_tweet_id with 'tweets[0].id'
            db_user.newest_tweet_id = tweets[0].id
        for tweet in tweets:
            # Get embedding for tweet, and store in db
            embedding = BASILICA.embed_sentence(tweet.full_text,
                                                model='twitter')
            db_tweet = Tweet(id=tweet.id, text=tweet.full_text[:500],
                             embeddings=embedding)
            db_user.tweets.append(db_tweet) # appending tweet
            DB.session.add(db_tweet) # adding tweet as its own entity in db
    except Exception as e:
        print('Error processing {}: {}'.format(username, e))
        raise e # the exception errow will show up as well
    else:
        # if no errors happen then commit it to Database
        DB.session.commit()