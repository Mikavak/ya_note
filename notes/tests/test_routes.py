from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..models import Note

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

    def test_pages_availability_for_auth_user(self):
        """
        Аутентифицированному пользователю доступна страница
        со списком заметок notes/, страница успешного добавления
        заметки done/, страница добавления новой заметки add/.
        """
        urls = (
            ('notes:list'),
            ('notes:success'),
            ('notes:add'),
        )
        for name in urls:
            self.client.force_login(self.author)
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        """
        Страницы отдельной заметки, удаления и редактирования заметки
        доступны только автору заметки. Если на эти страницы попытается 
        зайти другой пользователь — вернётся ошибка 404.
        """
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
        """
        При попытке перейти на страницу списка заметок,
        страницу успешного добавления записи, страницу 
        добавления заметки, отдельной заметки, редактирования
        или удаления заметки анонимный пользователь перенаправляется
        на страницу логина.
        """
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

    def test_home_page_and_registration_page_anonymous_client(self):
        """
        Главная страница доступна анонимному пользователю.
        Страницы регистрации пользователей, входа в 
        учётную запись и выхода из неё доступны всем пользователям.
        """
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
            