from django.test import Client, TestCase
from django.urls import reverse


class AboutViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.reverse_names = {
            'about/author.html': 'about:author',
            'about/tech.html': 'about:tech',
        }

    def test_about_pages_accessible_by_name(self):
        """
        Проверка, что для отображения страниц приложения about применяются
        ожидаемые view-функции
        """
        for name in self.reverse_names.values():
            with self.subTest(name=name):
                response = self.guest_client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_about_pages_use_correct_template(self):
        """
        Проверка, что для отображения страниц приложения about
        используются корректные шаблоны
        """
        for template, rev in self.reverse_names.items():
            with self.subTest():
                response = self.guest_client.get(reverse(rev))
                self.assertTemplateUsed(response, template)
