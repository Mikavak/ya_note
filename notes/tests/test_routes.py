from http import HTTPStatus
from ..models import Note
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='автор заметки')
        cls.reader = User.objects.create(username='НЕ автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='1')

    def test_pages_availability(self):
        urls = (
            ('notes:list'),
            ('notes:success'),
            ('notes:add'),
        )
        for name in urls:
            with self.subTest(name=name):
                self.client.force_login(self.author)
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author(self):
        urls = (
            ('notes:edit'),
            ('notes:detail'),
            ('notes:delete'),
        )

        for name in urls:
            self.client.force_login(self.reader)
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug))
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_for_anonymous_client(self):
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),

        )
        login_url = reverse('users:login')
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_home_page_and_registration_page(self):
        urls = (
            ('notes:home'),
            ('users:login'),
            ('users:logout'),
            ('users:signup'),
        )
        for name in urls:
            url = reverse(name)
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

