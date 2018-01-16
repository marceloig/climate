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
        self.climate_test = dict(date='1111-11-11', rainfall=20, temperature=40)
        with climate.app.app_context():
            climate.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(climate.app.config['DATABASE'])

    def test_url_invalid(self):
        rv = self.app.get('/')
        assert rv.status_code == 404

    def test_save_climate(self):
        rv = self.app.post('/climate', data=json.dumps(self.climate_test), content_type='application/json')
        assert rv.status_code == 201
    
    def test_save_invalid_climate(self):
        climate_invalid = dict(date='1111111', rainfall="20", temperature=True)
        rv = self.app.post('/climate', data=json.dumps(climate_invalid), content_type='application/json')
        assert rv.status_code == 201
    
    def test_get_climate_by_id(self):
        rv = self.app.post('/climate', data=json.dumps(self.climate_test), content_type='application/json')
        result_json = json.loads(rv.data)
        rv = self.app.get('/climate/{}'.format(result_json['id']))
        assert result_json['date'] == self.climate_test['date']
        assert result_json['temperature'] == self.climate_test['temperature']

    def test_get_climate_invalid(self):
        rv = self.app.get('/climate/{}'.format('q'))
        result_json = json.loads(rv.data)
        assert rv.status_code == 404
    
    def test_delete_climate(self):
        rv = self.app.post('/climate', data=json.dumps(self.climate_test), content_type='application/json')
        result_json = json.loads(rv.data)
        rv = self.app.delete('/climate/{}'.format(result_json['id']))
        result_json = json.loads(rv.data)
        assert result_json['message'] == "Success"
        assert rv.status_code == 200

if __name__ == '__main__':
    unittest.main()