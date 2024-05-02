# на страницы создания и редактирования заметки передаются формы.
from django.test import TestCase
from ..models import Note
from django.contrib.auth import get_user_model
from django.urls import reverse

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
        cls.note_2 = Note.objects.create(
            title='Новая заметка автора № 2',
            text='Текст',
            author=cls.author_2,
        )

    def test_note(self):
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

# в список заметок одного пользователя не попадают
# заметки другого пользователя;    
    def test_author(self):
        