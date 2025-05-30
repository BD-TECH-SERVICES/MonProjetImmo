from django.test import TestCase
from django.urls import reverse

class ViewTests(TestCase):
    def test_inscription_page_get(self):
        response = self.client.get(reverse('inscription'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_static_pages_get(self):
        self.assertEqual(self.client.get(reverse('nos_missions')).status_code, 200)
        self.assertEqual(self.client.get(reverse('credit')).status_code, 200)

    def test_protected_views_redirect(self):
        response = self.client.get(reverse('parcours'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

        response = self.client.get(reverse('profession'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)


