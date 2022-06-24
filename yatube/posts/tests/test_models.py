from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_model_post_have_correct_objects_names(self):
        '''Проверяем соответствие полей и названий в модели'''
        post = PostModelTest.post.text
        group = PostModelTest.group.title
        strings = {
            post: 'Тестовый пост',
            group: 'Тестовая группа',
        }
        for field, expected_value in strings.items():
            with self.subTest(field=field):
                self.assertEqual(
                    field[:15], expected_value[:15])

    def test_correct_verbose_name(self):
        '''Проверяем verbose_name в модели'''
        post = PostModelTest.post
        fields_verbose_names = {
            'text': 'Текст',
            'group': 'Группа',
        }
        for field, name in fields_verbose_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, name
                )

    def test_correct_help_text(self):
        '''Проверяем help_text в модели'''
        post = PostModelTest.post
        fields_help_text = {
            'text': 'Текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, name in fields_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(post._meta.get_field(field).help_text, name)
