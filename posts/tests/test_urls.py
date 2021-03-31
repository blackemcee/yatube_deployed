from django.test import TestCase, Client

from posts.models import Group, User, Post


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-slug',
            description='Test description'
        )
        cls.post = Post.objects.create(
            text='Пушкин',
            pub_date='2020-01-01',
            author=User.objects.create(username='test'),
            group=cls.group
        )
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='blackemcee')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.open_urls_list = ['/', '/group/test-slug/',
                              f'/{cls.post.author.username}/',
                              f'/test/{cls.post.pk}/']
        cls.auth_urls_list = ['/new/']

    def test_guest_urls_availability(self):
        """
        Проверка доступности основных страниц для неавторизованных
        пользователей
        """
        # __import__('pdb').set_trace()
        for urls in StaticURLTests.open_urls_list:
            with self.subTest():
                response_guest = StaticURLTests.guest_client.get(urls)
                self.assertEqual(response_guest.status_code, 200)
        for urls in StaticURLTests.auth_urls_list:
            with self.subTest():
                response_guest = StaticURLTests.guest_client.get(urls)
                self.assertRedirects(response_guest, '/auth/login/?next=/new/')

    def test_auth_urls_availability(self):
        """
        Проверка доступности всех страниц для авторизованных
        пользователей
        """
        for urls in (StaticURLTests.open_urls_list
                     + StaticURLTests.auth_urls_list):
            response_auth = StaticURLTests.authorized_client.get(urls)
            self.assertEqual(response_auth.status_code, 200)

    def test_urls_use_correct_templates(self):
        """
        Проверка использования корректных шаблонов для основных страниц
        """
        authorized_client = Client()
        authorized_client.force_login(StaticURLTests.post.author)
        templates_url_names = {
            'index.html': '/',
            'group.html': '/group/test-slug/',
            'new.html': (
                '/new/',
                f'/test/{StaticURLTests.post.pk}/edit/'
            )
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                if isinstance(reverse_name, tuple):
                    for addr in reverse_name:
                        response = authorized_client.get(addr)
                        self.assertTemplateUsed(response, template)
                else:
                    response = authorized_client.get(reverse_name)
                    self.assertTemplateUsed(response, template)

    def test_page_edit_behavior(self):
        """
        Проверка того, как ведет себя страница редактирования постов для
        неавторизованных пользователей, авторизованных, пытающихся
        отредактировать чужой пост и авторизованных, пытающихся
        отредактировать свой пост
        """
        guest_client = StaticURLTests.guest_client
        non_author_client = StaticURLTests.authorized_client
        author_client = Client()
        author_client.force_login(StaticURLTests.post.author)
        path = f'/test/{StaticURLTests.post.pk}/edit/'
        response_guest = guest_client.get(path)
        response_non_author = non_author_client.get(path)
        response_author = author_client.get(path)
        self.assertRedirects(response_guest, f'/auth/login/?next={path}')
        self.assertEqual(response_author.status_code, 200)
        self.assertRedirects(response_non_author,
                             f'/test/{StaticURLTests.post.pk}/')

    def test_check_404_code(self):
        """
        Проверка, возвращает ли сервер код 404 если ошибка не найдена
        """
        path = '/check/page/that/does/not/exist/'
        response = StaticURLTests.guest_client.get(path)
        self.assertEqual(response.status_code, 404)
