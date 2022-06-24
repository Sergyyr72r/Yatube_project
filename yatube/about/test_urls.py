from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse


class AboutUrlTest(TestCase):

    def test_url_author_exist(self):
        '''Проверяем наличие author и tech'''
        reverse_url = {
            'about:author': HTTPStatus.OK,
            'about:tech': HTTPStatus.OK,
        }
        for url, status in reverse_url.items():
            with self.subTest(url=url):
                response = self.client.get(reverse(url))
                self.assertEqual(response.status_code, status)

    def test_url_template(self):
        template_set = (
            ('about:author', 'about/author.html'),
            ('about:tech', 'about/tech.html'),
        )
        for url, template in template_set:
            with self.subTest(url=url):
                response = self.client.get(reverse(url))
                self.assertTemplateUsed(response, template)

    def test_url_hardurl(self):
        url_set = (
            ('about:author', '/about/author/'),
            ('about:tech', '/about/tech/')
        )
        for url, hardurl in url_set:
            with self.subTest(url=url):
                self.assertEqual(
                    reverse(url), hardurl
                )
