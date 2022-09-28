import os
from flask import Flask, request, jsonify, redirect
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db


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

@app.route('/api/users', methods=['POST'])
def create_user():
    return "User created"

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return "User retrieved"

@app.route('/api/users/<int:user_id>', methods=['PATCH'])
def update_user(user_id):
    return "User updated"

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    return "User deleted"

@app.route('/api/audio/<int:user_id>', methods=['POST'])
def insert_audio_data(user_id):
    return "Audio data added"

@app.route('/api/users/<int:user_id>/audio', methods=['GET'])
def get_audio_data(user_id):
    return "Audio data retrieved"

@app.route('/api/users/<int:user_id>/<int:session_id>', methods=['PATCH'])
def update_audio_data(user_id, session_id):
    return "Audio data updated"

