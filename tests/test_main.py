####
# Imports
####

import os
import unittest

from project import app, db
from project._config import basedir
from project.models import User


####
# Config
####

TEST_DB = 'test.db'


####
# Tests
####

class MainTests(unittest.TestCase):

    # setup and teardown

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()
        self.assertEquals(app.debug, False)


    def tearDown(self):
        db.session.remove()
        db.drop_all()


    # helper methods

    def login(self, name, password):
        return self.app.post('/', data=dict(
            name=name, password=password), follow_redirects=True)


    # tests

    def test_404_error(self):
        response = self.app.get('/this-route-does-not-exist/')
        self.assertEquals(response.status_code, 404)
        self.assertIn(b'Sorry. There\'s nothing here.', response.data)


    def test_500_error(self):
        bad_user = User(
            name='Howard',
            email='ho@ward.com',
            password='password'
        )
        db.session.add(bad_user)
        db.session.commit()
        self.assertRaises(ValueError, self.login, 'Howard', 'password')
        try:
            response = self.login('Howard', 'password')
            self.assertEquals(response.status_code, 500)
        except ValueError:
            pass


if __name__ == '__main__':
    unittest.main()
