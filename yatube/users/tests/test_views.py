from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


class UsersPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='auth')

    def setUp(self):
        self.user = User.objects.get(username='auth')
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user)

    def test_views_templates(self):
        '''Проверяем шаблон в signup Users'''
        response = self.authorised_client.get(reverse('users:signup'))
        self.assertTemplateUsed(response, 'users/signup.html')
