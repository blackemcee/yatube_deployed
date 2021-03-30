from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.group = Group.objects.create(
            title='Пушкин',
            slug='push',
            description='Это сообщество про Пушкина'
        )
        author = User.objects.create(username='test')
        for i in range(13):
            Post.objects.create(
                text='Пушкин' + str(i),
                author=author,
                group=cls.group
            )

    def test_first_page_contains_ten_records(self):
        """Проверка, что пагинатор выдает на первую страницу 10 постов"""
        response = PaginatorViewsTest.client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_contains_three_records(self):
        """
        Проверка, что пагинатор выдает на вторую страницу оставшиеся 3
        поста
        """
        response = PaginatorViewsTest.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
