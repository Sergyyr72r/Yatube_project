import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Post, Group, Follow

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_2 = User.objects.create_user(username='not_auth')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group_1 = Group.objects.create(
            title='Тестовая группа1',
            slug='test_slug1',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test_slug2',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group_1,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user)
        self.not_author_client = Client()
        self.not_author_client.force_login(self.user_2)

    def check_content(self, response, bool=False):
        if bool is True:
            test_obj = response.context['post']
        else:
            test_obj = response.context['page_obj'][0]
        context_dict = {
            test_obj.author: self.user,
            test_obj.group: self.group_1,
            test_obj.text: self.post.text,
            test_obj.pub_date: self.post.pub_date,
            test_obj.image: self.post.image,
        }
        for param, expected in context_dict.items():
            with self.subTest(param=param):
                self.assertEqual(param, expected)
                self.assertContains(response, '<img')

    def test_index_content(self):
        '''Проверяем контекст index'''
        response = self.authorised_client.get(reverse('posts:index'))
        self.check_content(response)

    def test_group_context(self):
        '''Проверяем контекст group'''
        response = self.authorised_client.get(
            reverse('posts:group', args=(self.group_1.slug,))
        )
        group = response.context['group']
        self.assertEqual(group, self.group_1)
        self.check_content(response)

    def test_profile_context(self):
        '''Проверяем контекст profile'''
        response = self.authorised_client.get(
            reverse('posts:profile', args=(self.user.username,))
        )
        author = response.context['author']
        self.assertEqual(author, self.user)
        self.check_content(response)

    def test_post_context(self):
        '''Проверяем контекст post'''
        response = self.authorised_client.get(
            reverse('posts:post_detail', args=(self.post.id,))
        )
        self.check_content(response, True)

    def test_post_to_the_right_group(self):
        '''Проверяем, что пост создан с верной группой'''
        Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group_2,
        )
        group = Group.objects.create(
            title='Тестовая группа3',
            slug='test_slug3',
            description='Тестовое описание',
        )
        response = self.authorised_client.get(
            reverse('posts:group', args=(group.slug,))
        )
        self.assertEqual(response.context['page_obj'].paginator.count, 0)
        response = self.authorised_client.get(
            reverse('posts:group', args=(self.group_2.slug,))
        )
        self.assertEqual(response.context['page_obj'].paginator.count, 1)

    def test_post_create_edit_correct_constext(self):
        '''Проверяем контекст post_create и post_edit'''
        urls_set = (
            ('posts:post_create', (None)),
            ('posts:post_edit', (self.post.id,))
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.ImageField,
        }
        for url, arg in urls_set:
            with self.subTest(url=url):
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        response = self.authorised_client.get(
                            reverse(url, args=arg)
                        )
                        form_field = response.context.get(
                            'form').fields.get(value)
                        self.assertIsInstance(form_field, expected)
                        form = response.context.get(
                            'form')
                        self.assertIsInstance(form, PostForm)

    def test_post_delete(self):
        '''Тест удаление поста'''
        Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group_1,
        )
        count = Post.objects.count()
        self.client.post(reverse(
            'posts:post_detail', args=(self.post.id,)), follow=True,
        )
        self.assertEqual(Post.objects.count(), count)
        self.not_author_client.post(reverse(
            'posts:post_detail', args=(self.post.id,))
        )
        self.assertEqual(Post.objects.count(), count)
        self.authorised_client.post(reverse(
            'posts:post_detail', args=(self.post.id,))
        )
        self.assertEqual(Post.objects.count(), 1)

    def test_cache(self):
        '''Тест кэширования'''
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group_1,
        )
        response = self.client.get(reverse('posts:index'))
        post.delete()
        response_after_deletion = self.client.get(reverse('posts:index'))
        self.assertEqual(response.content, response_after_deletion.content)
        cache.clear()
        response_clear_cache = self.client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, response_clear_cache.content)

    def test_posts_subsctibed(self):
        '''Тест постов подписки'''
        self.authorised_client.post(reverse(
            'posts:profile_follow', args=(self.user_2.username,)),
        )
        response = self.authorised_client.get(reverse(
            'posts:follow_index')
        )
        self.assertEqual(
            response.context['page_obj'].paginator.count,
            self.user_2.posts.count()
        )
        response = self.not_author_client.get(reverse(
            'posts:follow_index')
        )
        self.assertEqual(
            response.context['page_obj'].paginator.count, 0
        )

    def test_subscription(self):
        '''Проверяем подписки'''
        self.authorised_client.post(reverse(
            'posts:profile_follow', args=(self.user_2.username,)),
        )
        self.assertIs(
            Follow.objects.filter(user=self.user, author=self.user_2).exists(),
            True
        )

    def test_unsubscription(self):
        '''Проверяем отписки'''
        Follow.objects.create(
            user=self.user,
            author=self.user_2
        )
        self.authorised_client.post(reverse(
            'posts:profile_unfollow', args=(self.user_2.username,)),
        )
        self.assertIs(
            Follow.objects.filter(user=self.user, author=self.user_2).exists(),
            False
        )

    def test_self_subscription(self):
        '''Проверяем подписки на себя'''
        self.authorised_client.post(reverse(
            'posts:profile_follow', args=(self.user.username,)),
        )
        self.assertIs(
            Follow.objects.filter(user=self.user, author=self.user_2).exists(),
            False
        )

    def test_self_one_subscription(self):
        '''Проверяем возможность повторной подписки'''
        count = self.user.following.count()
        self.authorised_client.post(reverse(
            'posts:profile_follow', args=(self.user_2.username,)),
        )
        self.assertEqual(count, self.user.following.count())


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        POST_NUMBER = 15
        cls.user = User.objects.create_user(username='auth_2')
        cls.user_2 = User.objects.create_user(username='auth_3')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        for number in range(POST_NUMBER):
            Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group,
            )

    def setUp(self):
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user)
        self.authorised_client_2 = Client()
        self.authorised_client_2.force_login(self.user_2)
        Follow.objects.create(
            user=self.user_2,
            author=self.user,
        )

    def test_paginator(self):
        '''Проверяем paginator'''
        urls_set = (
            ('posts:index', None),
            ('posts:profile', (self.user.username,)),
            ('posts:group', (self.group.slug,)),
            ('posts:follow_index', None),
        )
        pages_set = (
            ('?page=1', settings.POSTS_NUMBER),
            ('?page=2', Post.objects.count() - settings.POSTS_NUMBER),
        )
        for url, arg in urls_set:
            with self.subTest(url=url):
                for page, number in pages_set:
                    with self.subTest(page=page):
                        if url == 'posts:follow_index':
                            response = self.authorised_client_2.get(
                                reverse(url, args=arg) + page
                            )
                            self.assertEqual(len(
                                response.context['page_obj']), number
                            )
                        else:
                            response = self.authorised_client.get(
                                reverse(url, args=arg) + page
                            )
                            self.assertEqual(len(
                                response.context['page_obj']), number
                            )
