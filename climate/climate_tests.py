import os
import climate
import unittest
import tempfile
import json

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, climate.app.config['DATABASE'] = tempfile.mkstemp()
        climate.app.testing = True
        self.app = climate.app.test_client()
        with climate.app.app_context():
            climate.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(climate.app.config['DATABASE'])

    def test_url_invalid(self):
        rv = self.app.get('/')
        assert rv.status_code == 404

    def test_save_climate(self):
        climate = {'date': '11/11/1111', 'rainfall': 20, 'temperature': 40}
        rv = self.app.post('/climate', data = json.dumps(climate))
        assert rv.status_code == 200

if __name__ == '__main__':
    unittest.main()