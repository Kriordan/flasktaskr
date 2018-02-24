import os
import unittest

from project import app, db
from project._config import basedir
from project.models import User

TEST_DB = 'test.db'


class TasksTests(unittest.TestCase):

    # setup and teardown

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        db.create_all()


    def tearDown(self):
        db.session.remove()
        db.drop_all()


    # helper methods

    def login(self, name, password):
        return self.app.post('/', data=dict(
            name=name, password=password), follow_redirects=True)


    def register(self, name, email, password, confirm):
        return self.app.post(
            'register/',
            data=dict(name=name, email=email, password=password, confirm=confirm),
            follow_redirects=True
        )


    def logout(self):
        return self.app.get('logout/', follow_redirects=True)


    def create_user(self, name, email, password):
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()


    def create_admin_user(self):
        new_user = User(
            name="Superman",
            email="admin@test.com",
            password="password",
            role="admin"
        )
        db.session.add(new_user)
        db.session.commit()


    def create_task(self):
        return self.app.post('add/', data=dict(
            name='Go to the bank',
            due_date='10/31/2018',
            priority='1',
            posted_date='02/12/2018',
            status='1',
        ), follow_redirects=True)


    # tests

    def test_logged_in_users_can_access_tasks_page(self):
        self.register('Christopher', 'chris@test.com', 'password', 'password')
        self.login('Christopher', 'password')
        response = self.app.get('tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add a new task:', response.data)


    def test_not_logged_in_users_cannot_access_tasks_page(self):
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertIn(b'You need to login first.', response.data)


    def test_users_can_add_tasks(self):
        self.create_user('Christopher', 'chris@test.com', 'password')
        self.login('Christopher', 'password')
        self.app.get('tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn(
            b'New entry was successfully posted!',
            response.data
        )


    def test_users_cannot_add_tasks_when_error(self):
        self.create_user('Christopher', 'chris@test.com', 'password')
        self.login('Christopher', 'password')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.post('add/', data=dict(
            name='Go to the bank',
            due_date = '',
            priority='1',
            posted_date='02/18/2018',
            status='1'
        ), follow_redirects=True)
        self.assertIn(b'This field is required.', response.data)


    def test_users_can_complete_tasks(self):
        self.create_user('Christopher', 'chris@test.com', 'password')
        self.login('Christopher', 'password')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get('complete/1/', follow_redirects=True)
        self.assertIn(b'The task is complete. Nice.', response.data)


    def test_users_can_delete_tasks(self):
        self.create_user('Christopher', 'chris@test.com', 'password')
        self.login('Christopher', 'password')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        response = self.app.get('delete/1/', follow_redirects=True)
        self.assertIn(b'The task was deleted.', response.data)


    def test_users_cannot_complete_tasks_that_are_not_created_by_them(self):
        self.create_user('Christopher', 'chris@test.com', 'password')
        self.login('Christopher', 'password')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user('Samuel', 'sam@test.com', 'password')
        self.login('Samuel', 'password')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get('complete/1/', follow_redirects=True)
        self.assertNotIn(b'The task is complete. Nice.', response.data)
        self.assertIn(b'You can only update tasks that belong to you.',
                      response.data)


    def test_users_cannot_delete_tasks_that_are_not_created_by_them(self):
        self.create_user('Christopher', 'chris@test.com', 'password')
        self.login('Christopher', 'password')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_user('Samuel', 'sam@test.com', 'password')
        self.login('Samuel', 'password')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get('delete/1/', follow_redirects=True)
        self.assertIn(b'You can only delete tasks that belong to you.',
                      response.data)


    def test_admin_users_can_complete_tasks_that_are_not_created_by_them(self):
        self.create_user('Christopher', 'chris@test.com', 'password')
        self.login('Christopher', 'password')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'password')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get('complete/1/', follow_redirects=True)
        self.assertNotIn(b'You can only update tasks that belong to you.',
                         response.data)


    def test_admin_users_can_delete_tasks_that_are_not_created_by_them(self):
        self.create_user('Christopher', 'chris@test.com', 'password')
        self.login('Christopher', 'password')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'password')
        self.app.get('tasks/', follow_redirects=True)
        response = self.app.get('delete/1/', follow_redirects=True)
        self.assertNotIn(b'You can only delete tasks that belong to you.',
                         response.data)


    def test_task_template_displays_logged_in_user_name(self):
        self.register(
            'Christopher', 'chris@test.com', 'password', 'password'
        )
        self.login('Christopher', 'password')
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertIn(b'Christopher', response.data)


    def test_users_cannot_see_task_modify_links_for_tasks_not_created_by_them(self):
        self.register('Howard', 'ho@ward.com', 'password', 'password')
        self.login('Howard', 'password')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.register('Hamlet', 'ham@let.com', 'password', 'password')
        self.login('Hamlet', 'password')
        response = self.app.get('tasks/', follow_redirects=True)
        self.assertNotIn(b'Complete', response.data)
        self.assertNotIn(b'Delete', response.data)


    def test_users_can_see_task_modify_links_for_tasks_created_by_them(self):
        self.register('Howard', 'ho@ward.com', 'password', 'password')
        self.login('Howard', 'password')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.register('Hamlet', 'ham@let.com', 'password', 'password')
        self.login('Hamlet', 'password')
        self.app.get('tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn(b'complete/2/', response.data)
        self.assertIn(b'delete/2/', response.data)


    def test_admin_users_can_see_task_modify_links_for_all_tasks(self):
        self.register('Howard', 'ho@ward.com', 'password', 'password')
        self.login('Howard', 'password')
        self.app.get('tasks/', follow_redirects=True)
        self.create_task()
        self.logout()
        self.create_admin_user()
        self.login('Superman', 'password')
        self.app.get('tasks/', follow_redirects=True)
        response = self.create_task()
        self.assertIn(b'complete/1/', response.data)
        self.assertIn(b'delete/1/', response.data)
        self.assertIn(b'complete/2/', response.data)
        self.assertIn(b'delete/2/', response.data)


if __name__ == "__main__":
    unittest.main()
