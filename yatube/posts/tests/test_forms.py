import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post

User = get_user_model()


# В конце добавил тесты для проверки комментариев
class PostsFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.not_author = User.objects.create_user(username='passenger')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)

    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Описание тестовой группы'
        )
        self.post = Post.objects.create(
            text='Исходный текст',
            author=self.user,
        )

    def test_create_post(self):
        posts_count = Post.objects.count()
        """Валидная форма создает пост"""
        form_data = {
            'text': 'Новый пост',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=(self.user,))
        )

        new_post = Post.objects.select_related('group').order_by('-id')[0]
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group.id, form_data['group'])

    def test_edit_post(self):
        """Валидная форма редактирует пост"""
        form_data = {
            'text': 'Измененный текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args={self.post.id, }),
            data=form_data,
        )

        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(self.post.id,))
        )
        edited_post = Post.objects.select_related('group').get(id=self.post.id)
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.group.id, form_data['group'])

    def test_unauthorized_user_create_post(self):
        posts_count = Post.objects.count()
        """Неавторизованый пользователь не может создать пост"""
        form_data = {
            'text': 'Жалкая попытка',
            'group': self.group.id,
        }
        self.client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_unauthorized_edit_post(self):
        """Неавторизованый пользователь не может редактировать пост"""
        source_text = self.post.text
        sorce_group = self.post.group
        form_data = {
            'text': 'Измененный текст',
            'group': self.group.id,
        }
        self.client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
        )
        edited_post = Post.objects.select_related('group').get(id=self.post.id)
        self.assertEqual(edited_post.text, source_text)
        self.assertEqual(edited_post.group, sorce_group)

    def test_not_author_edit_post(self):
        """Не автор поста не может редактировать пост"""
        source_text = self.post.text
        sorce_group = self.post.group
        form_data = {
            'text': 'Измененный текст',
            'group': self.group.id,
        }
        self.not_author_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
        )
        edited_post = Post.objects.select_related('group').get(id=self.post.id)
        self.assertEqual(edited_post.text, source_text)
        self.assertEqual(edited_post.group, sorce_group)

# Вот они
    def test_comment_form_work_correct(self):
        """Форма комментария работает правильно"""
        comments_count = Comment.objects.filter(post=self.post).count()
        form_data = {
            'text': 'Коммантарий к посту'
        }
        self.authorized_client.post(
            reverse('posts:add_comment', args={self.post.id}),
            data=form_data,
        )
        response = self.authorized_client.get(
            reverse('posts:post_detail', args={self.post.id})
        )
        self.assertEqual(
            Comment.objects.filter(post=self.post).count(),
            comments_count + 1
        )
        self.assertEqual(
            response.context['comments'][0].text,
            form_data['text']
        )

    def test_comment_unauthorized_fail(self):
        comments_count = Comment.objects.filter(post=self.post).count()
        form_data = {
            'text': 'Коммантарий к посту'
        }
        self.client.post(
            reverse('posts:add_comment', args={self.post.id}),
            data=form_data,
        )
        self.assertEqual(
            Comment.objects.filter(post=self.post).count(),
            comments_count
        )


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsImagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='tester')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Описание тестовой группы'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_new_post_with_img(self):
        """Форма с картинкой создает пост в БД"""
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'title': 'Тестовый заголовок',
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=(self.user.username,))
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_post_with_image(self):
        """При выводе поста с картинкой изображение
        передается в контексте
        """
        adress_list = [
            reverse('posts:index'),
            reverse('posts:group_list', args=(self.group.slug,)),
            reverse('posts:profile', args=(self.user.username,)),
        ]
        for adress in adress_list:
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTrue(response.context.get('page_obj')[0].image)
