from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


class UserUrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.authorised_client = Client()
        self.authorised_client.force_login(UserUrlTest.user)

    def test_url_access(self):
        response_dict = {
            'users:logout': HTTPStatus.OK,
            'users:signup': HTTPStatus.OK,
            'users:login': HTTPStatus.OK,
            'users:password_change': HTTPStatus.FOUND,
            'users:password_change_done': HTTPStatus.FOUND,
            'users:password_reset': HTTPStatus.OK,
            'users:password_reset_done': HTTPStatus.OK,
            'users:password_reset_complete': HTTPStatus.OK,
        }
        for url, status in response_dict.items():
            with self.subTest(url=url):
                response = self.authorised_client.get(reverse(url))
                self.assertEqual(response.status_code, status)

    def test_url_templates(self):
        templates_dict = {
            'users:logout': 'users/logged_out.html',
            'users:login': 'users/login.html',
            'users:password_reset': 'users/password_reset_form.html',
            'users:password_reset_done': 'users/password_reset_done.html',
            'users:password_reset_complete':
            'users/password_reset_complete.html',
        }
        for url, template in templates_dict.items():
            with self.subTest(url=url):
                response = self.authorised_client.get(reverse(url))
                self.assertTemplateUsed(response, template)
