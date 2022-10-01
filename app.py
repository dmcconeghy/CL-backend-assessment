import os
from flask import Flask, request, json
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import exc
from models import db, connect_db, User, Audio, Tick

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
    """
        Creates a new user from params: name, email, address, and image. 
        All fields are required. 
        Duplicate emails are rejected. 
        Returns a string of the user's data.

    """

    name = request.args.get('name')
    email = request.args.get('email')
    address = request.args.get('address')
    image = request.args.get('image')

    # More complex validation errors could be incorporated here.
    if not name or not email or not address or not image:
        return "Missing required field"

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
    except exc.IntegrityError:
        # Prevent a DB error from being returned to the user if their email is already in use.
          
        return "A user with that email already exists."
    
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):

    """
        Given a user_id, return the user's basic information.
    
    """

    user = User.query.get_or_404(user_id)

    # This could be returned as formatted JSON instead.
    # We can also call a helper function to restore the audio data.   
    return f"User retrieved: {user}" 

@app.route('/api/users/<int:user_id>', methods=['PATCH'])
def update_user(user_id):

    """
        Patch route updates user information. 
        Accepts inputs for name, email, address, or image. 
    
    """

    user = User.query.get_or_404(user_id)

    # Use the pre-existing field data if a field isn't supplied with an update to its entry. 

    user.name = request.args.get('name') or user.name
    user.email = request.args.get('email') or user.email
    user.address = request.args.get('address') or user.address
    user.image = request.args.get('image') or user.image

    db.session.commit()

    return f"Updated {user}"
    
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
        Deletes the user with the given user_id. 
    
    """

    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return f"User {user_id} deleted"

# AUDIO API ROUTES [POST, GET, PATCH]

@app.route('/api/audio', methods=['POST'])
def insert_audio_data():
    """
        
        Creates a new audio entry from params: 
            user_id, session_id, selected_tick, and step_count. 

            For example,

            {   
                "user_id": 5,
                ticks": [-96.33, -96.33, -93.47, -89.03999999999999, -84.61, -80.18, -75.75, -71.32, -66.89, -62.46, -58.03, -53.6, -49.17, -44.74, -40.31], 
                "selected_tick": 5, 
                "session_id": 3448, 
                "step_count": 1
            }

        All fields are required, including a user_id. 

        Additional validation: 
            “Ticks” must be 15 values and range from -10.0 to -100.0.
            “Session_id” must be unique.
            “Step_count” must be unique for every “session_id” and be 0 to 9 in value.
            “Selected_tick” values must be between 0 and 14.

        Ticks are stored in their own, related table. 

        Returns the audio data as a string.
 
    """

    input_string = request.get_json()

    session_id = input_string['session_id']
    user_id = input_string['user_id']
    selected_tick = input_string['selected_tick']
    step_count = input_string['step_count']
    ticks = input_string['ticks']

    # More complex validation errors could be incorporated here.
    if not user_id:
        return "Missing required user_id."
    if step_count not in range(0, 10):
        return "Step count must be between 0 and 9"
    if selected_tick not in range(0, 15):
        return "Selected tick must be between 0 and 14"
    if len(ticks) != 15:
        return "Ticks must be an array of 15 values"
    
    try: 
        new_audio = Audio(
            session_id = session_id,
            user_id = user_id,
            selected_tick = selected_tick,
            step_count = step_count
        )

        try: 
            for tick in ticks:

                new_Tick = Tick(
                    session_id = session_id,
                    tick = float(tick),
                )

                db.session.add(new_Tick)
        except exc.IntegrityError:
           return "Error adding tick data"

        db.session.add(new_audio)
        
        db.session.commit()

        return f"Audio data created {new_audio}"
  
    except exc.IntegrityError:

        return "Session IDs must be unique."

@app.route('/api/audio/<int:user_id>', methods=['GET'])
def get_audio_data_by_user(user_id):
    """
        Given a user_id, return an array of user audio data sessions. 
    
    """
    
    audio = Audio.query.filter(Audio.user_id == user_id).all()

    # return f"Audio data for user #{user_id} : {Audio.__repr__(audio)}"
    return f"Here's the data for user #{user_id}'s sessions: {audio}"

@app.route('/api/audio/session/<int:session_id>', methods=['GET'])
def get_audio_data_by_session(session_id):
    """
        Given a session_id, return the audio data.
        Doubles as a search route, returning a 404 if there is no such session. 
    
    """
    
    audio = Audio.query.get_or_404(session_id)

    return f"Here's the session: \n {audio}"

@app.route('/api/audio/update/<int:session_id>', methods=['PATCH'])
def update_audio_data(session_id):

    """
        Patch route updates audio data. 
        Accepts changes to step_count, selected_tick, or ticks.
        * Option to change session id will require updating all a session's ticks.
        * We would also need to check for duplicate session ids before committing. 
        The ticks array will be overwritten with the newer values.  

        Returns the audio object's repr. 
    
    """

    audio = Audio.query.get_or_404(session_id)

    # Check for a valid new step_count value
    if not request.args.get('step_count'):
        pass
    elif int(request.args.get('step_count')) not in range(0, 10):
        return "Step count must be between 0 and 9"
    else:
        audio.step_count = request.args.get('step_count')

    # Check for a valid new selected_tick value
    if not request.args.get('selected_tick'):
        pass
    elif int(request.args.get('selected_tick')) not in range(0, 15):
        return "Selected tick must be between 0 and 14"
    else:
        audio.selected_tick = request.args.get('selected_tick')
 
    # Check to see if new ticks were supplied
    if not request.args.get('ticks'):
        pass
    else:

        updated_ticks_string = request.args.get('ticks')
        updated_ticks = updated_ticks_string.split(',')
        updated_ticks = [float(tick) for tick in updated_ticks]

        if len(updated_ticks) != 15:
            
            return f"Ticks must be an array of 15 values"
         

        original_ticks = Tick.query.filter(Tick.session_id == session_id).all()

        for t in range (0, 15):
            if updated_ticks[t] > -10.0 or updated_ticks[t] < -100.0:
                return f"Ticks must be between -10.0 and -100.0"

            original_ticks[t] = updated_ticks[t]
        
    db.session.commit()

    return f"Updated {audio}"
    
    
# USERS API SEARCH ROUTES [GET by id, name, email, or address]
# These items can be condensed into a single route with a query string.

@app.route('/api/users/search/id', methods=['GET'])
def search_by_user_id(id):

    id = request.args.get('id')

    try:

        user = User.query.get_or_404(id)
        return f"{User.__repr__(user)}"
    except exc.IntegrityError:
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

# Ports for GCP deployment?
# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 8080))
#     app.run(debug=True, host="0.0.0.0", port=port)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')