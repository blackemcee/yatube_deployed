from django.test import TestCase

from posts.models import Group, Post, User


class GroupPostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Пушкин',
            slug='push',
            description='Это сообщество про Пушкина'
        )
        cls.post = Post.objects.create(
            text='Пушкин',
            author=User.objects.create(username='test'),
            group=cls.group
        )

    def test_verbose_name(self):
        """Проверка корректности содержимого поля verbose для постов"""
        post = GroupPostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'group': 'Название сообщества',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(post._meta.get_field(value).verbose_name,
                                 expected)

    def test_help_text(self):
        """Проверка корректности содержимого поля help_text для постов"""
        post = GroupPostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Введите имя группы',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(post._meta.get_field(value).help_text,
                                 expected)

    def test_post_str_method(self):
        """Проверка, что str сокращает текст поста до 15 символов"""
        post = GroupPostModelTest.post
        self.assertEqual(str(post), post.text[:15])

    def test_group_str_method(self):
        """Проверка, что str корректно выдает название группы"""
        group = GroupPostModelTest.group
        self.assertEqual(str(group), group.title)
