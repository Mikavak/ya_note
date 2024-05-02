# news/tests/test_logic.py
# from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify
from http import HTTPStatus

from ..forms import WARNING
# Импортируем из файла с формами список стоп-слов и предупреждение формы.
# Загляните в news/forms.py, разберитесь с их назначением.
# from news.forms import BAD_WORDS, WARNING
from ..models import Note

User = get_user_model()


class TestCommentCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.url_2 = reverse('notes:success')
        cls.author = User.objects.create(username='Залогиненый')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.form_data = {'title': 'New',
                         'text': 'Новая заметка', 'author': cls.author}
        cls.note = Note.objects.create(
            title='Заметка',
            text='текст заметки',
            author=cls.author)

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_user_can_create_comment(self):
        self.auth_client.post(self.url, data=self.form_data)

        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_slug(self):
        note = Note.objects.create(
            title='F', text='f', author=self.user, slug='1')
        self.form_data['slug'] = '1'
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(response, 'form', 'slug',
                             errors=(note.slug + WARNING))

    def test_empty_slug(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_other_user_cant_edit_note(self):
        urls = (
            ('notes:edit'),
            ('notes:detail'),
        )
        for name in urls:
            response = self.client.post(name, data=self.form_data)
            self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_author_can_delete_note(self):
        urls = (
            ('notes:edit'),
            ('notes:delete'),
        )
        for name in urls:
            url = reverse(name, args=(note.slug))
            response = self.auth_client.post(url, data=self.form_data)
            self.assertRedirects(response, reverse('notes:success'))
