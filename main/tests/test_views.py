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
        static_pages = [
            'nos_missions', 'credit', 'achat', 'vente', 'investissement',
            'primo_accedant', 'notre_mission', 'nos_partenaires',
            'temoignages', 'contact'
        ]
        for name in static_pages:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_protected_views_redirect(self):
        response = self.client.get(reverse('parcours'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

        response = self.client.get(reverse('profession'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)


