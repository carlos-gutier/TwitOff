"""Prediction of Users based on Tweet embeddings."""
import numpy as np
from sklearn.linear_model import LogisticRegression
from .models import User
from .twitter import BASILICA

# The predict is being called with 2 user names and tweet text to predict
def predict_user(user1_name, user2_name, tweet_text):
    """Determine and return which user is more likely to say a given Tweet."""
    # With imported 'User' model we get the 'user' object
    user1 = User.query.filter(User.name == user1_name).one()
    user2 = User.query.filter(User.name == user2_name).one()
    # Get their embeddings that are already in db and collect them in numpy array
    user1_embeddings = np.array([tweet.embeddings for tweet in user1.tweets])
    user2_embeddings = np.array([tweet.embeddings for tweet in user2.tweets])
    # 'vstack' vertically stacks the embeddings all together
    # into a gigiant embeddings matrix - with all rows of user1 embeddings
    # and then all rows user2 embeddings
    embeddings = np.vstack([user1_embeddings, user2_embeddings])
    # Then we make the labels: user1 gets 1 & user2 gets 0
    # number of labels for each depends on number of tweets each has
    labels = np.concatenate([np.ones(len(user1.tweets)),
                             np.zeros(len(user2.tweets))])
    # Running logistic regression (Scikit-learn classification model)
    log_reg = LogisticRegression().fit(embeddings, labels)
    # below: 'embeddings' is X and 'labels' is Y
    # Hitting Basilica API to get embeddings for the sentence we're predicting
    tweet_embedding = BASILICA.embed_sentence(tweet_text, model='twitter')
    # Making prediction
    return log_reg.predict(np.array(tweet_embedding).reshape(1, -1))