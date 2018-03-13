from django.test import TestCase
from django.test.client import Client

# Create your tests here.

class ViewTest(TestCase):
    def setUp(self):
       self.client = Client()

    def test_register_page(self):
        data = {'username': 'test_user',
                'email': 'test_user@example.com',
                'password1': 'pass123',
                #'password2': 'pass123'
                }
        response = self.client.post('/register/',data)
        self.assertEqual(response.status_code,200)

    def test_bookmark_save(self):
        # response = self.client.login('habib','smirk200')
        # self.assertTrue(response)

        data = {
               'url': 'http://www.example.com/',
               'title': 'Test URL',
               'tags': 'test-tag'
               }

        response = self.client.post('/save/', data)
        self.assertEqual(response.status_code, 302)
        # response = self.client.get('/user/habib/')
        # self.assertTrue('http://www.example.com/' in response.content)
        # self.assertTrue('Test URL' in response.content)
        # self.assertTrue('test-tag' in response.content)
