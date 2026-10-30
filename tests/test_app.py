import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch('routes.events.fetch_all', return_value=[])
    def test_empty_event_list(self, fetch):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('目前沒有可報名的活動', response.text)

    @patch('routes.events.execute')
    def test_create_event(self, execute):
        response = self.client.post('/events', data={'title':'活動', 'description':'說明', 'location':'台北', 'event_date':'2026-12-01T10:00'}, follow_redirects=False)
        self.assertEqual(response.status_code, 303)

    @patch('routes.registrations.fetch_one', return_value={'event_id':1, 'title':'活動', 'status':'open'})
    @patch('routes.registrations.execute', return_value=1)
    def test_register(self, execute, fetch):
        response = self.client.post('/events/1/register', data={'name':'王小明', 'phone':'0912345678'}, follow_redirects=False)
        self.assertEqual(response.status_code, 303)

    @patch('routes.registrations.fetch_one', return_value={'event_id':1, 'title':'活動', 'status':'closed'})
    def test_closed_event_cannot_register(self, fetch):
        self.assertEqual(self.client.get('/events/1/register').status_code, 400)

    @patch('routes.registrations.fetch_all', return_value=[{'name':'王小明','phone':'0912345678','created_at':'2026-01-01'}])
    @patch('routes.registrations.fetch_one', return_value={'event_id':1,'title':'活動','status':'open'})
    def test_attendees(self, fetch, fetch_all):
        response = self.client.get('/events/1/attendees')
        self.assertEqual(response.status_code, 200)
        self.assertIn('王小明', response.text)

if __name__ == '__main__': unittest.main()
