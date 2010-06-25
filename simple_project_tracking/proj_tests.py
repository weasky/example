import config
import os
import proj
import unittest
import tempfile

class ProjTestCase(unittest.TestCase):

    def setUp(self):
        ''' Create new test client and database before each test.
        '''
        self.db_fd, proj.app.config['DATABASE'] = tempfile.mkstemp()
        self.app = proj.app.test_client()
        proj.init_db()

    def tearDown(self):
        ''' Remove database after each test.
        '''
        os.close(self.db_fd)
        os.unlink(proj.app.config['DATABASE'])
        
    def test_empty_db(self):
        resp = self.app.get('/')
        assert 'Nothing here yet!' in resp.data
        
    def test_login_logout(self):
        resp = self.app.post('/login', data=dict(
                username=config.USERNAME,
                password=config.PASSWORD, 
            ), follow_redirects=True)
        assert 'You were logged in' in resp.data
        resp = self.app.get('/logout', follow_redirects=True)
        assert 'You were logged out' in resp.data

        resp = self.app.post('/login', data=dict(
                username='this is not a real username',
                password=config.PASSWORD, 
            ), follow_redirects=True)
        assert 'Invalid username' in resp.data
        
        resp = self.app.post('/login', data=dict(
                username=config.USERNAME,
                password='this is not a real password', 
            ), follow_redirects=True)
        assert 'Invalid password' in resp.data
        

if __name__ == '__main__':
    unittest.main()
