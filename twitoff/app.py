"""Main application and routing logic for TwitOff."""
from decouple import config
from flask import Flask, render_template, request
from .models import DB, User
from .predict import predict_user
from .twitter import add_or_update_user


def create_app():
    """Create and configure and instance of the Flask application"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    DB.init_app(app)

    @app.route('/')
    def root():
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)
    
    # to add users (POST resquest below) 
    # we don't need URL parameter '/<name>'
    # because to add users we'll have a form
    @app.route('/user', methods=['POST']) 
    @app.route('/user/<name>', methods=['GET']) # to get users - GET request
    def user(name=None): # Name needs 'None' default value since it may not exist
        message = ''
        
        # import pdb; pdb.set_trace() # Python debugger swapped by 'name' line below
        
        # if there is a name in GET request (populated name is true)
        # than name equals name, otherwise name is a POST request
        name = name or request.values['user_name']
        # we want to be able to add new user
        # but adding a user can fail, user may not exist 
        # or account may be private
        try:
            # we add user if request method is POST
            if request.method == 'POST': 
                # here same method can add or update user
                # so it's not destructive if accidentally called multiple times
                add_or_update_user(name) 
                message = 'User {} successfully added!'.format(name)
            # Whether or not we add user we still get that user's tweets so we set 'tweets'
            # '.one()' below raises exception if user not found
            #  instead of '.first()' that would return None if not found
            tweets = User.query.filter(User.name == name).one().tweets 
        except Exception as e:
            message = 'Error adding {}: {}'.format(name, e) # name of user & error message
            tweets = [] # here we'll pass on the tweets we get
        # we return a 'user' template/html with user name, tweets, and message    
        return render_template('user.html', title=name, tweets=tweets,
                               message=message)

    @app.route('/compare', methods=['POST'])
    def compare():
        user1, user2 = request.values['user1'], request.values['user2']
        if user1 == user2:
            return 'Cannot compare a user to themselves!'
        else:
            prediction = predict_user(user1, user2,
                                      request.values['tweet_text'])
            return user1 if prediction else user2    
    
    # here you should add a decorator @loginrequired to not leave this open!
    # for only admin users with privilidge to reset database
    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template('base.html', title='DB Reset!', users=[])

    return app


