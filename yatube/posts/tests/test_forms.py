from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, Comment

User = get_user_model()


class PostCreateTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group_1 = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа_2',
            slug='test_slug_2',
            description='Тестовое описание_2',
        )
        cls.post = Post.objects.create(
            author=User.objects.get(username='auth'),
            text='Тестовый пост',
            group=cls.group_1,
        )

    def setUp(self):
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user)

    def test_authorised_post_creation(self):
        '''Проверяем создание поста'''
        count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'group': self.group_1.id,
        }
        response = self.authorised_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', args=(self.user.username,))
        )
        post = Post.objects.first()
        post_data = {
            form_data['text']: post.text,
            form_data['group']: post.group.id,
        }
        for data_post, data_form in post_data.items():
            with self.subTest(data_post=data_post):
                self.assertEqual(data_post, data_form)
        self.assertEqual(Post.objects.count(), count + 1)

    def test_unauthorised_post_creation(self):
        count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
        }
        self.client.post(reverse('posts:post_create'),
                         data=form_data,
                         follow=True,
                         )
        self.assertEqual(Post.objects.count(), count)

    def test_post_edit(self):
        '''Проверяем редактирование поста'''
        form_data = {
            'text': 'Новый текст поста',
            'group': self.group_2.id,
        }
        self.authorised_client.post(
            reverse('posts:post_edit',
                    args=(self.post.pk,)),
            data=form_data,
            follow=True,
        )
        request = self.authorised_client.get(
            reverse('posts:group',
                    args=(self.group_1.slug,)
                    )
        )
        self.assertEqual(request.context['page_obj'].paginator.count, 0)
        post = Post.objects.first()
        edited_post = {
            post.text: form_data['text'],
            post.group.id: form_data['group'],
            post.author: self.user,
        }
        for field, data in edited_post.items():
            with self.subTest(field=field):
                self.assertEqual(field, data)
        self.assertEqual(Post.objects.count(), 1)

    def test_comment_create(self):
        form_data = {
            'text': 'test_text',
        }
        count = Comment.objects.count()
        self.client.post(
            reverse('posts:add_comment',
                    args=(self.post.pk,)),
            data=form_data,
            follow=True,
        )
        self.assertEqual(count, Comment.objects.count())
        self.authorised_client.post(
            reverse('posts:add_comment',
                    args=(self.post.pk,)),
            data=form_data,
            follow=True,
        )
        self.assertEqual(count + 1, Comment.objects.count())
