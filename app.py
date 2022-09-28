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
# These items will be condensed into a single route with a query string, but I wanted to begin using different routes for each search parameter.

@app.route('/api/users/search/id', methods=['GET'])
def search_by_user_id(id):

    id = request.args.get('id')

    try:

        user = User.query.get_or_404(id)
        return f"{User.__repr__(user)}"
    except IntegrityError:
        return "No users found"

@app.route('/api/users/search/name', methods=['GET'])
def search_by_user_name():
    """
        This route uses SQL %LIKE% to search for a user by name.
        It will return the first user that matches the search query.
        It does not currently return multiple matches. 
    
    """

    name = request.args.get('name')

    user = User.query.filter(User.name.like(f"%{name}%")).first()

    if not user:
        return "No users found"
    else:
        return f"{User.__repr__(user)}"
            
@app.route('/api/users/search/email', methods=['GET'])
def search_by_user_email():
    """
        This route uses SQL %LIKE% to search for a user by email.
        It will return the first user that matches the search query.
        It does not currently return multiple matches. 
    
    """

    email = request.args.get('email')

    user = User.query.filter(User.email.like(f"%{email}%")).first()

    if not user:
        return "No users found."
    else:
        return f"{User.__repr__(user)}"

@app.route('/api/users/search/address', methods=['GET'])
def search_by_user_address():
    """
        This route uses SQL %LIKE% to search for a user by address.
        It will return the first user that matches the search query.
        It does not currently return multiple matches. 
    
    """

    address = request.args.get('address')

    user = User.query.filter(User.address.like(f"%{address}%")).first()

    if not user:
        return "No users found."
    else:
        return f"{User.__repr__(user)}"

# AUDIO API SEARCH ROUTES [GET by session_id]

# @app.route('/api/audio/search/<int:session_id>', methods=['GET'])
# def search_by_session_id(session_id):

#     # This will be updated to return a list of audio data for a given session_id

#     # user = User.query.filter_by(User.session_id=session_id).first()


#     # This should be updated to return the audio data rather than the user. 
#     return f"{User.__repr__(user)}"
