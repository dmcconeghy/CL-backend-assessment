from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_db(app):

    db.app = app
    db.init_app(app)

class User(db.Model):
    """ 
        User Model includes id, name, email, address, image, and, by relation, audio data.
           
         # Address could be divided into street, city, state, zip, etc.
        # We can also use a separate table for address
        # We can decide on a max string length for the address later. 
        # Image is a string of the image file name

    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    address = db.Column(db.String, nullable=False)
    image = db.Column(db.String(100), nullable=False)
    audio = db.relationship('Audio')

    def __repr__(self):
        return f"Name: {self.name}, Email: {self.email}, Address: {self.address}, Image: {self.image}"


class Audio(db.Model):
    """ 

        Audio Model includes "session_id"(key), user_id(foreign key), "selected_tick", "step_count", and, by relation, "ticks".

    """

    __tablename__ = 'audio'

    session_id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False )
    selected_tick = db.Column(db.Integer, nullable=False)
    step_count = db.Column(db.Integer, nullable=False)
    

    def __repr__(self):
        return f''' Session ID: {self.session_id}, 
                    User ID: {self.user_id}, 
                    Selected Tick: {self.selected_tick}, 
                    Step Count: {self.step_count}, 
                    Ticks: {Tick.compile_ticks_by_session(self.session_id)}'''

    
    # It seems a natural next step to deliver a user's multiple sessions. 


class Tick(db.Model):
    """
    
        Ticks is an intersection table between Audio and Users. 
        It includes unique "ticks_id"(key), an audio "session_id"(key) matched with a user_id, and "tick" value.
        The array of multiple ticks that enters as JSON is parsed into this table and refereced against the audio session_id.
    
    """

    __tablename__ = 'ticks'

    ticks_id = db.Column(db.Integer, autoincrement=True)
    session_id = db.Column(db.Integer, db.ForeignKey('audio.session_id'), nullable=False)
    tick = db.Column(db.Numeric, nullable=False)
    db.PrimaryKeyConstraint(ticks_id, session_id)
    ticks = db.relationship('Audio', backref='ticks')


    def compile_ticks_by_session(session_id):
        ticks = Tick.query.filter(Tick.session_id == session_id).all()
        output = [float(t.tick) for t in ticks]
        return output
        