from django.test import TestCase
from django.urls import reverse

class ViewTests(TestCase):
    def test_inscription_page_get(self):
        response = self.client.get(reverse('inscription'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

