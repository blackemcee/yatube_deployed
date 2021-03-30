from django.test import Client, TestCase


class AboutUrlsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.urls_list = ['/about/author/', '/about/tech/']
        self.templates = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/'
        }

    def test_about_url_exists_at_desired_location(self):
        """
        Проверка, что страницы приложения about доступны любому
        пользователю
        """
        for url in self.urls_list:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_about_url_uses_correct_template(self):
        """Проверка, что страницы приложения about корректные шаблоны"""
        for template, path in self.templates.items():
            with self.subTest():
                response = self.guest_client.get(path)
                self.assertTemplateUsed(response, template)
