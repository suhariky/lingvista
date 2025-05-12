from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import LanguageLevel, Profile


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.profile = Profile.objects.create(user=self.user)
        self.language_level = LanguageLevel.objects.create(level='A1')

    def test_public_views(self):
        response = self.client.get(reverse('main_page'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('private_policy'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('login'))
        self.assertContains(response, 'Username')

        response = self.client.get(reverse('register'))
        self.assertContains(response, 'Email')

    def test_auth_redirects(self):
        protected_urls = [reverse('profile_view'), reverse('langlevel')]

        for url in protected_urls:
            response = self.client.get(url)
            self.assertRedirects(response, f"{reverse('login')}?next={url}")

    def test_authenticated_views(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile_view'))
        self.assertContains(response, 'testuser')
        response = self.client.get(reverse('langlevel'))
        self.assertContains(response, 'A1')

    def test_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('main_page'))
