import os
import shutil

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Post, User


@override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'temp_forms'))
class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.user = User.objects.create_user(username='blackemcee')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
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
        self.form_data = {
            'text': 'Тестовый пост',
            'group': '',
            'image': uploaded
        }
        self.form = PostCreateFormTest.authorized_client.post(
            reverse('new_post'),
            data=self.form_data,
            follow=True
        )

    def test_create_post(self):
        """
        Проверка, что при создании нового поста появляется
        новая запись в БД
        """
        posts_count = Post.objects.count()

        form = PostCreateFormTest.authorized_client.post(
            reverse('new_post'),
            data=self.form_data,
            follow=True
        )
        self.assertRedirects(form, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        """
        Проверка, что при редактировании существующего поста изменяется
        соответствующая запись в БД
        """
        new_form_data = {
            'text': 'Обновленный пост',
            'group': ''
        }
        PostCreateFormTest.authorized_client.post(
            reverse('post_edit', kwargs={
                'username': PostCreateFormTest.user.username,
                'post_id': Post.objects.last().id,
            }),
            data=new_form_data,
            follow=True
        )
        updated_post = Post.objects.last()
        updated_text_value = updated_post.__dict__['text']
        self.assertEqual(updated_text_value, new_form_data['text'])
