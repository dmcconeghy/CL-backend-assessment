import os
from unittest import TestCase
from models import db, User, Audio, Tick

# This DATABASE_URL will cause testing faiures. 
# The host "db" can't be found, but I am unsure how to correctly reference the db container's host ip.
# The tests work locally with a local install of appropriate psql databases. 
# The database works locally and successfully spins up the database. 
# But this path doesn't work in the containers.  
# os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@db:5432/postgres'

# For offline local testing. 
os.environ['DATABASE_URL'] = "postgresql:///cl_backend_test"

from app import app

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

class AppTest(TestCase):
    """
        Tests the POST route for AUDIO
    
    """

    def setUp(self):
        """
            Add sample user
        """
        
        User.query.delete()
        Audio.query.delete()
        Tick.query.delete()

    def tearDown(self):
        """
            Clean up any fouled transactions
        """
        db.session.rollback()
  
    def test_bad_session_id_404(self):
        """
            Does the server return a 404 if the audio session_id is not found?
        """
        with app.test_client() as client:

            resp = client.get('/api/audio/session/8675309', follow_redirects=True)
            # html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 404)

    def test_create_audio(self):
        """
            Does the server create a new audio data from the POST route?
            
            Create a user. Verify their user_id. 
            Create audio data for that user. Verify that the audio data exists.
        """
        with app.test_client() as client:
            resp = client.post('/api/users?name=Bob%20Marley&email=jamaica%40email.com&address=Sandy%20Beaches&image=pictureofme.com/image.jpg', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            

            payload = f"{{\"user_id\": 1,\n \"ticks\": [-66.33, -66.33, -63.47, -69.03999999999999, -84.61, -80.18, -75.75, -71.32, -66.89, -62.46, -58.03, -53.6, -49.17, -44.74, -40.31], \"selected_tick\": 5, \"session_id\": 99999, \"step_count\": 0\n}}"

            resp = client.post(f"/api/audio", data = payload, content_type='application/json')
            # resp = client.get(f"/api/audio/1", content_type='application/json')
            html = resp.get_data(as_text=True)
            self.assertIn('99999', html)

    def test_get_audio(self):
        """
            Does the server return audio data from the db?

            First create a test user with audio data. 
            Then fetch the session directly. 
        """
        with app.test_client() as client:

            resp = client.post('/api/users?name=Bob%20Marley&email=jamaica%40email.com&address=Sandy%20Beaches&image=pictureofme.com/image.jpg', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            

            payload = f"{{\"user_id\": 2,\n \"ticks\": [-66.33, -66.33, -63.47, -69.03999999999999, -84.61, -80.18, -75.75, -71.32, -66.89, -62.46, -58.03, -53.6, -49.17, -44.74, -40.31], \"selected_tick\": 5, \"session_id\": 88888, \"step_count\": 0\n}}"

            resp = client.post(f"/api/audio", data = payload, content_type='application/json')
            self.assertEqual(resp.status_code, 200)

            resp = client.get('/api/audio/session/88888', follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Session ID: 88888', html)

    def test_update_audio(self):
        """
            With a created user and audio data, can we patch the data?

            Create a user. Create their audio. Check that they exist. 
            Update their audio data. Check that it was updated.
            
        
        """

        with app.test_client() as client: 

            resp = client.post('/api/users?name=Bob%20Marley&email=jamaica%40email.com&address=Sandy%20Beaches&image=pictureofme.com/image.jpg', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            

            payload = f"{{\"user_id\": 3,\n \"ticks\": [-66.33, -66.33, -63.47, -69.03999999999999, -84.61, -80.18, -75.75, -71.32, -66.89, -62.46, -58.03, -53.6, -49.17, -44.74, -40.31], \"selected_tick\": 5, \"session_id\": 77777, \"step_count\": 0\n}}"

            resp = client.post(f"/api/audio", data = payload, content_type='application/json')
            self.assertEqual(resp.status_code, 200)


            # Tests 'Selected Tick' & 'Step Count' parameters
            # BEFORE
            resp = client.get('/api/audio/session/77777', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('Selected Tick: 5', html)
            self.assertIn('Step Count: 0', html)

            # AFTER
            resp = client.patch("/api/audio/update/77777?step_count=7&selected_tick=7", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn(f"Selected Tick: 7", html)
            self.assertIn(f"Step Count: 7", html)

            resp = client.patch('/api/audio/update/77777?ticks=-11.11,%20-11.11,%20-11.11,%20-11.11,%20-11.11,%20-11.11,%20-11.11,%20-11.11,%20-11.11,%20-11.11,%20-11.11,%20-11.11,%20-11.11,%20-11.11,%20-11.11', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn(f"Ticks: [-11", html)
