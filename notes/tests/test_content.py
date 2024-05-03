from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='автор № 1')
        cls.author_2 = User.objects.create(username='автор № 2')
        cls.note = Note.objects.create(
            title='Новая заметка автора № 1',
            text='Текст',
            author=cls.author,
        )

    def test_note(self):
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_author(self):
        self.client.force_login(self.author_2)
        response = self.client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_authorized_client_has_form(self):
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:add', None)
        )
        for name, args in urls:
            self.client.force_login(self.author)
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
