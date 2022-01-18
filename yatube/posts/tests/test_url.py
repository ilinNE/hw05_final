from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):

    def test_author(self):
        """Проверка статических страниц"""
        adress_list = [reverse('about:author'), reverse('about:tech')]
        for adress in adress_list:
            with self.subTest(adress=adress):
                response = self.client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='testuser')
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Описание тестовой группы'

        )
        cls.post = Post.objects.create(
            text='Тестовый текст c текстом',
            author=cls.author,
            group=cls.test_group

        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author_client = Client()
        self.authorized_author_client.force_login(self.author)

    def test_posts_urls_exists_at_desired_locations(self):
        """Проверяем общедоступные страницы"""
        adress_list = [
            reverse('posts:index'),
            reverse('posts:group_list', args=(self.test_group.slug,)),
            reverse('posts:profile', args=(self.user.username,)),
            reverse('posts:post_detail', args=(self.post.id,))
        ]
        for adress in adress_list:
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_create_url_for_authorized_user_exist(self):
        """Страница создания нового поста доступна
        для авторизованого пользовавтеля
        """
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_edit_post_url_for_author_exist(self):
        """Страница редактирования поста доступна для автора поста"""
        response = self.authorized_author_client.get(
            reverse('posts:post_edit', args=(self.post.id,))
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_redirects_url(self):
        """С адресов с ограниченым доступом пользолватель
        без достурпа перенаправляется по правильным адресам
        """
        redirect_dict = {
            reverse('posts:post_create'):
                reverse('users:login')
                + '?next=' + reverse('posts:post_create'),
            reverse('posts:post_edit', args=(self.post.id,)):
                reverse('users:login')
                + '?next=' + reverse('posts:post_edit', args=(self.post.id,)),
        }
        for adress, redirect in redirect_dict.items():
            with self.subTest(adress=adress):
                response = self.client.get(adress, follow=True)
                self.assertRedirects(response, redirect)

    def test_posts_templates_exist(self):
        """По всем адресам находятся правильные шаблоны"""
        templates_dict = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    args=(self.test_group.slug,)): 'posts/group_list.html',
            reverse('posts:profile',
                    args=(self.user.username,)): 'posts/profile.html',
            reverse('posts:post_detail',
                    args=(self.post.id,)): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    args=(self.post.id,)): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for adress, template in templates_dict.items():
            with self.subTest(adress=adress):
                response = self.authorized_author_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_unexsisted_page(self):
        """Несуществующая страница показывает код 404"""
        response = self.authorized_client.get('/unexcisted/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
