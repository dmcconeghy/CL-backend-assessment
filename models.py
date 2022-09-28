from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_db(app):

    db.app = app
    db.init_app(app)

class User(db.Model):
    """ 
        User Model has two parts:
            Basic information: id, name, email, address, and image
            JSON audio data as follows: 

                '{
                    "ticks": [-96.33, -96.33, -93.47, -89.03999999999999, -84.61, -80.18, -75.75, -71.32, -66.89, -62.46, -58.03, -53.6, -49.17, -44.74, -40.31], 
                    “selected_tick”: 5, 
                    "session_id": 3448, 
                    "step_count": 1
                }'
    
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)

    # Address could be divided into street, city, state, zip, etc.
    # We can also use a separate table for address
    # We can decide on a max string length for the address later. 
    address = db.Column(db.String, nullable=False)
    
    # Image is a string of the image file name
    image = db.Column(db.String(100), nullable=False)
    audio_data = db.Column(db.String) 
    # Will audio_data always be included at the time of user creation? Or will it be added later? 
    # Should audio_data be a separate table by reference to user id?
