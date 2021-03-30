import os
import shutil

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.cache import cache

from posts.models import Group, Post, User, Follow


@override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'temp_views'))
class GroupPostModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Пушкин',
            slug='push',
            description='Это сообщество про Пушкина'
        )
        cls.post = Post.objects.create(
            text='Пушкин',
            pub_date='2020-01-01',
            author=User.objects.create(username='test'),
            group=cls.group,
            image=uploaded
        )
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='blackemcee')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.open_urls_list = ['/', '/group/test-slug/']
        cls.auth_urls_list = ['/new/']

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_pages_use_correct_template(self):
        """
        Проверка того, что при обращении к view-классам через
        соответствующий name будет вызван корректный шаблон
        """
        template_pages_names = {
            'index.html': reverse('index'),
            'group.html': (reverse('groups', kwargs={'slug': 'push'})),
            'posts/new.html': reverse('new_post'),
        }
        for template, reverse_name in template_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_homepage_shows_correct_context(self):
        """
        Проверка того, что главная страница получает
        корректный контекст
        """
        response = GroupPostModelTests.authorized_client.get(reverse('index'))
        post = GroupPostModelTests.post
        response_post = response.context['page'][0]
        self.assertEqual(post, response_post)

    def test_group_shows_correct_context(self):
        """
        Проверка того, что страница сообщества получает
        корректный контекст
        """
        response = GroupPostModelTests.authorized_client.get(reverse(
            'groups', kwargs={'slug': 'push'}))
        post = GroupPostModelTests.post
        group = GroupPostModelTests.group
        response_post = response.context['page'][0]
        response_group = response.context['group']
        self.assertEqual(post, response_post)
        self.assertEqual(group, response_group)

    def test_new_post_shows_correct_context(self):
        """
        Проверка того, что страница создания нового поста получает
        корректный контекст
        """
        response = GroupPostModelTests.authorized_client.get(reverse(
            'new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_does_not_go_to_incorrect_group(self):
        """
        Проверка того, что новосозданный пост не попадает в чужое
        сообщество
        """
        self.wrong_group = Group.objects.create(
            title='Пелевин',
            slug='pel',
            description='Это сообщество про Пелевина'
        )
        post = GroupPostModelTests.post
        response = GroupPostModelTests.authorized_client.get(reverse(
            'groups', kwargs={'slug': 'pel'}))
        response_post = response.context['page']
        self.assertNotEqual(post, response_post)

    def test_edit_post_shows_correct_context(self):
        """
        Проверка того, что страница редактирования поста получает
        корректный контекст
        """
        authorized_client = Client()
        authorized_client.force_login(GroupPostModelTests.post.author)
        response = authorized_client.get(
            reverse('post_edit', kwargs={
                'username': GroupPostModelTests.post.author,
                'post_id': GroupPostModelTests.post.id
            }))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_user_profile_shows_correct_context(self):
        """
        Проверка того, что страница пользовательского профиля получает
        корректный контекст
        """
        response = GroupPostModelTests.authorized_client.get(reverse(
            'profile', kwargs={'username': GroupPostModelTests.post.author}))
        post = GroupPostModelTests.post
        response_post = response.context['page'][0]
        self.assertEqual(post, response_post)

    def test_post_view_shows_correct_context(self):
        """
        Проверка того, что страница отдельного поста получает
        корректный контекст
        """
        response = GroupPostModelTests.authorized_client.get(reverse(
            'post', kwargs={'username': GroupPostModelTests.post.author,
                            'post_id': GroupPostModelTests.post.id}))
        post = GroupPostModelTests.post
        response_post = response.context['post']
        self.assertEqual(post, response_post)

    def test_index_cache(self):
        """Проверка кеширования записей на главной странице"""
        initial_response = GroupPostModelTests.authorized_client.get(
            reverse('index')).content
        Post.objects.create(
            text='Тестовый пост',
            author=GroupPostModelTests.user
        )
        new_response = GroupPostModelTests.authorized_client.get(reverse(
            'index')).content
        self.assertEqual(initial_response, new_response)
        cache.clear()
        response_with_new_post = GroupPostModelTests.authorized_client.get(
            reverse('index')).content
        self.assertNotEqual(new_response, response_with_new_post)

    def test_user_can_follow_unfollow(self):
        """
        Проверка, что авторизованный пользователь может
        подписываться на других пользователей и удалять их из подписок
        """
        GroupPostModelTests.authorized_client.get(reverse(
            'profile_follow',
            kwargs={'username': GroupPostModelTests.post.author}))
        link = Follow.objects.filter(
            user=GroupPostModelTests.user,
            author__username=GroupPostModelTests.post.author).count()
        self.assertEqual(link, 1)
        GroupPostModelTests.authorized_client.get(reverse(
            'profile_unfollow',
            kwargs={'username': GroupPostModelTests.post.author}))
        link = Follow.objects.filter(
            user=GroupPostModelTests.user,
            author__username=GroupPostModelTests.post.author).count()
        self.assertEqual(link, 0)

    def test_user_sees_followed_posts(self):
        """
        Проверка, что новая запись пользователя появляется
        в ленте тех, кто на него подписан и не появляется в ленте тех,
        кто не подписан на него
        """
        GroupPostModelTests.authorized_client.get(reverse(
            'profile_follow',
            kwargs={'username': GroupPostModelTests.post.author}))
        response = GroupPostModelTests.authorized_client.get(reverse(
            'follow_index'))
        post = GroupPostModelTests.post
        response_post = response.context['page'][0]
        self.assertEqual(post, response_post)

        other_user = User.objects.create_user(username='other_user')
        other_authorized_client = Client()
        other_authorized_client.force_login(other_user)
        response = other_authorized_client.get(reverse('follow_index'))
        with self.assertRaises(IndexError):
            response.context['page'][0]

    def test_who_can_commnet_under_posts(self):
        """
        Проверка, что только авторизованный пользователь может
        комментировать посты
        """
        guest_client = GroupPostModelTests.guest_client
        auth_client = GroupPostModelTests.authorized_client
        path = (f'/{GroupPostModelTests.post.author}/'
                f'{GroupPostModelTests.post.id}/comment')
        response_guest = guest_client.get(path)
        self.assertRedirects(response_guest, f'/auth/login/?next={path}')
        response_auth = auth_client.get(path)
        self.assertEqual(response_auth.status_code, 200)
