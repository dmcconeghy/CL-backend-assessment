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
os.environ['DATABASE_URL'] = "postgresql:///c_labs"

from app import app

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

class AppTest(TestCase):
    """
        Tests the POST route for USERS
    
    """

    def setUp(self):
        """
            Clear the db before each unit test.
        """
        User.query.delete()
        Audio.query.delete()
        Tick.query.delete()

    def tearDown(self):
        """
            Clean up any fouled transactions after each test.
        """
        db.session.rollback()

    def test_server_response(self):
        """
            Is the server responsing at its root?
        """

        with app.test_client() as client:
            resp = client.get('/')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Ground Control to Major Tom', html)

    def test_bad_user_id_404(self):
        """
            Does the server return a 404 if the user id is not found?
        """
        with app.test_client() as client:

            resp = client.get('/api/users/999', follow_redirects=True)
            # html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 404)

    

    def test_create_user(self):
        """
            Does the server create a new user?
        """
        with app.test_client() as client:

            resp = client.post('/api/users?name=betty&email=betty%40email.com&address=9%20ash%20court&image=pictureofme.com/image.jpg', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('betty', html)

    def test_get_user(self):
        """
            Does the server return a user from the db?
        """
        with app.test_client() as client:

            resp = client.post('/api/users?name=timon&email=timon%40email.com&address=9%20ash%20court&image=pictureofme.com/image.jpg', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            user_id = User.query.filter_by(name='timon').first().id

            resp = client.get(f"/api/users/{user_id}", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('timon', html)

    def test_delete_user(self):
        """
            If we create a user and then delete them, do they 404?

            Create a user. Check that they exist. 
            Delete them. Check that they 404.
        
        """

        with app.test_client() as client:

            resp = client.post('/api/users?name=pumbaa&email=pumbaa%40email.com&address=9%20ash%20court&image=pictureofme.com/image.jpg', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            user_id = User.query.filter_by(name='pumbaa').first().id

            resp = client.get(f"/api/users/{user_id}", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertIn('pumbaa', html)

            resp = client.delete(f"/api/users/{user_id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn(f"User {user_id} deleted", html)

            resp = client.get(f"/api/users/{user_id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 404)
            
    def test_patch_user(self):
        """
            Can we update a user's information?

        """
        with app.test_client() as client:

            resp = client.post('/api/users?name=doctorwho&email=tardis%40email.com&address=TARDIS&image=pictureofme.com/image.jpg', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            user_id = User.query.filter_by(name='doctorwho').first().id

            resp = client.get(f"/api/users/{user_id}", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertIn('doctor', html)

            resp = client.patch(f"/api/users/{user_id}?name=themaster", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("themaster", html)

    def test_search_queries(self):
        """
            Do the endpoints for name/address/email return db results?
        
        """

        with app.test_client() as client:

            resp = client.post('/api/users?name=waldo&email=whereami%40email.com&address=Come%20and%20Find%20Me%20Circle&image=pictureofme.com/waldo.jpg', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            # user_id = User.query.filter_by(name='waldo').first().id

            resp = client.get("/api/users/search/name?name=waldo", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('waldo', html)

            resp = client.get("/api/users/search/address?address=Come%20and%20Find%20Me%20Circle", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('waldo', html)

            resp = client.get("/api/users/search/email?email=whereami%40email.com", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('waldo', html)
           

