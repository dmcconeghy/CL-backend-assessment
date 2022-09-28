import os
from flask import Flask, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User


uri = os.environ.get('DATABASE_URL', 'postgresql:///concha_labs')

if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'hear_clearly')
toolbar = DebugToolbarExtension(app)

connect_db(app)

db.create_all()

@app.route('/')
def home_page():
    return "Mission Control to Major Tom"

# USERS API ROUTES [POST, GET, PATCH, DELETE]

@app.route('/api/users', methods=['POST'])
def create_user():

    name = request.args.get('name')
    email = request.args.get('email')
    address = request.args.get('address')
    image = request.args.get('image')

    try: 
        new_user = User(
            name = name,
            email = email,
            address = address,
            image = image
        )

        db.session.add(new_user)
        db.session.commit()

        return f"User created {new_user}"
    except IntegrityError:
        # Adding complexity to our error feedback messages can be integrated with a front end forms and/or
        # We can treat the user information individually to make sure all are present before checking for potential duplicate emails.  
        return "A user with that email already exists or you are missing required inputs"
    
    
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):

    user = User.query.get_or_404(user_id)

    # This should be updated to return stringified, ideally with a User class method.  
    return f"User retrieved: {User.__repr__(user)}" 

@app.route('/api/users/<int:user_id>', methods=['PATCH'])
def update_user(user_id):

    user = User.query.get_or_404(user_id)

    user.name = request.args.get('name') or user.name
    user.email = request.args.get('email') or user.email
    user.address = request.args.get('address') or user.address
    user.image = request.args.get('image') or user.image

    db.session.commit()

    return f"Updated {User.__repr__(user)}"
    

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):

    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return f"User {user_id} deleted"

# AUDIO API ROUTES [POST, GET, PATCH]

@app.route('/api/audio/<int:session_id>', methods=['POST'])
def insert_audio_data(user_id):
    user = User.query.get_or_404(user_id)

    audio = user.audio_data or request.args.get()

    return f"{audio}" or "No audio data found"

@app.route('/api/audio/<int:user_id>/audio', methods=['GET'])
def read_audio_data(user_id):
    user = User.query.get_or_404(user_id)

    return f"{user.audio_data}" or "No audio data found"

@app.route('/api/audio/<int:user_id>/<int:session_id>', methods=['PATCH'])
def update_audio_data(user_id, session_id):
    return "Audio data updated"
    

# USERS API SEARCH ROUTES [GET by id, name, email, or address]
# These items will be condensed into a single route with a query string, but I wanted to begin using different routes for each search parameter

@app.route('/api/users/search_id/<int:id>', methods=['GET'])
def search_by_user_id(id):

    user = User.query.get_or_404(id)

    return f"{User.__repr__(user)}"

@app.route('/api/users/search_name/<string:name>', methods=['GET'])
def search_by_user_name(name):

    # .first() returns a single item, which is useful for testing. 
    # .all() returns a list of items, which needs to be iterated. 
    user = User.query.filter_by(User.name == name).first()
    return f"{User.__repr__(user)}"

@app.route('/api/users/search_email/<string:email>', methods=['GET'])
def search_by_user_email(email):

    user = User.query.filter_by(User.email == email).first()
    return f"{User.__repr__(user)}"

@app.route('/api/users/search_address/<string:address>', methods=['GET'])
def search_by_user_address(address):

    user = User.query.filter_by(User.address == address).first()
    return f"{User.__repr__(user)}"

# AUDIO API SEARCH ROUTES [GET by session_id]

# @app.route('/api/audio/search/<int:session_id>', methods=['GET'])
# def search_by_session_id(session_id):

#     # This will be updated to return a list of audio data for a given session_id

#     # user = User.query.filter_by(User.session_id=session_id).first()


#     # This should be updated to return the audio data rather than the user. 
#     return f"{User.__repr__(user)}"
