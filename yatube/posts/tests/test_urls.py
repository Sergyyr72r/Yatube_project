from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostsUrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_auth = User.objects.create_user(username='auth')
        cls.user_not_auth = User.objects.create_user(username='not_auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_auth,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorised_client_auth = Client()
        self.authorised_client_auth.force_login(PostsUrlTest.user_auth)
        self.authorised_client_not_auth = Client()
        self.authorised_client_not_auth.force_login(PostsUrlTest.user_not_auth)
        self.urls_list = (
            ('posts:index', None),
            ('posts:group', (self.group.slug,)),
            ('posts:profile', (self.user_auth.username,)),
            ('posts:post_edit', (self.post.id,)),
            ('posts:post_detail', (self.post.id,)),
            ('posts:post_create', None),
            ('posts:profile_follow', (self.user_not_auth.username,)),
            ('posts:profile_unfollow', (self.user_not_auth.username,)),
            ('posts:add_comment', (self.post.pk,)),
            ('posts:follow_index', None),
        )

    def test_url_hardurl(self):
        '''Проркрка соответствия url и hardurl'''
        urls_list = (
            ('posts:index', None, '/'),
            ('posts:group', (self.group.slug,), f'/group/{self.group.slug}/'),
            ('posts:profile', (self.user_auth.username,),
                f'/profile/{self.user_auth.username}/'),
            ('posts:post_edit', (self.post.id,),
                f'/posts/{self.post.id}/edit/'),
            ('posts:post_detail', (self.post.id,), f'/posts/{self.post.id}/'),
            ('posts:post_create', None, '/create/'),
            ('posts:profile_follow', (self.user_auth.username,),
                f'/profile/{self.user_auth.username}/follow/'),
            ('posts:profile_unfollow', (self.user_auth.username,),
                f'/profile/{self.user_auth.username}/unfollow/'),
            ('posts:add_comment', (self.post.pk,),
                f'/posts/{self.post.pk}/comment'),
            ('posts:follow_index', None, '/follow/'),
        )
        for name, arg, url in urls_list:
            with self.subTest(name=name):
                self.assertEqual(url, reverse(name, args=arg))

    def test_unathorised_access(self):
        '''Прроверка неавторизированного доступа'''
        for name, arg in self.urls_list:
            with self.subTest(name=name):
                response = self.client.get(
                    reverse(name, args=arg)
                )
                if name in ['posts:post_edit', 'posts:post_create',
                            'posts:add_comment', 'posts:profile_unfollow',
                            'posts:profile_follow', 'posts:follow_index'
                            ]:
                    redirect_name = reverse('users:login')
                    redirect_arg = reverse(name, args=arg)
                    target_url = f'{redirect_name}?next={redirect_arg}'
                    self.assertRedirects(
                        response, target_url
                    )
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_access(self):
        '''Прроверка доступа автора'''
        for name, arg in self.urls_list:
            with self.subTest(name=name):
                response = self.authorised_client_auth.get(
                    reverse(name, args=arg)
                )
                if name == 'posts:add_comment':
                    self.assertRedirects(response, reverse('posts:post_detail',
                                         args=(self.post.id,))
                                         )
                elif name in ['posts:profile_follow',
                              'posts:profile_unfollow'
                              ]:
                    self.assertRedirects(response, reverse('posts:profile',
                                         args=(self.user_auth.username,))
                                         )
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_not_author_access(self):
        '''Прроверка доступа не автора'''
        for name, arg in self.urls_list:
            with self.subTest(name=name):
                response = self.authorised_client_not_auth.get(
                    reverse(name, args=arg)
                )
                if name == 'posts:post_edit':
                    self.assertRedirects(
                        response, reverse(
                            'posts:post_detail', args=arg)
                    )
                elif name == 'posts:add_comment':
                    self.assertRedirects(response, reverse('posts:post_detail',
                                         args=(self.post.id,))
                                         )
                elif name in ['posts:profile_follow',
                              'posts:profile_unfollow'
                              ]:
                    self.assertRedirects(response, reverse('posts:profile',
                                         args=(self.user_not_auth.username,))
                                         )
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_templates(self):
        '''Проверяем шаблоны'''
        templates_list = (
            ('posts:index', None, 'posts/index.html'),
            ('posts:group', (self.group.slug,), 'posts/group_list.html'),
            ('posts:profile', (
                self.user_auth.username,), 'posts/profile.html'
             ),
            ('posts:post_edit', (self.post.id,), 'posts/create_post.html'),
            ('posts:post_detail', (self.post.id,), 'posts/post_detail.html'),
            ('posts:post_create', None, 'posts/create_post.html'),
            ('posts:follow_index', None, 'posts/follow.html'),
        )
        for url, arg, template in templates_list:
            with self.subTest(url=url):
                response = self.authorised_client_auth.get(
                    reverse(url, args=arg)
                )
                self.assertTemplateUsed(response, template)

    def test_errors_template404(self):
        '''Проверяем редирект ошибок 404'''
        response = self.client.get('/unknown_page')
        self.assertTemplateUsed(response, 'core/404.html')
