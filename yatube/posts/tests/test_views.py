from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='tester')
        cls.user2 = User.objects.create(username='noname')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Описание тестовой группы'
        )
        Post.objects.create(
            text='Тестовый текст c текстом',
            author=cls.user2,

        )
        cls.post = Post.objects.create(
            text='Тестовый текст c текстом',
            author=cls.user,
            group=cls.group

        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        Group.objects.create(
            title='Тестовая группа 2',
            slug='test-group-2',
            description='Описание тестовой группы'
        )

# Дописал здесь проверку шаблона 404
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    args=(self.group.slug,)): 'posts/group_list.html',
            reverse('posts:profile',
                    args=(self.user.username,)): 'posts/profile.html',
            reverse('posts:post_detail',
                    args=(self.post.id,)): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    args=(self.post.id,)): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            'unexisted/': 'core/404.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_index_show_correct_context(self):
        """На главной странице список постов"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_post = response.context['page_obj'][0]
        self.assertEqual(first_post.author.username, self.post.author.username)
        self.assertEqual(first_post.text, self.post.text)
        self.assertEqual(first_post.group.title, self.post.group.title)
        self.assertEqual(first_post.id, self.post.id)

    def test_posts_group_show_correct_context(self):
        """На странице группы только посты этой группы"""
        response = self.authorized_client.get(reverse(
            'posts:group_list', args=(self.group.slug,)))
        posts_set = response.context['page_obj']
        for post in posts_set:
            with self.subTest(post=post):
                self.assertEqual(post.group.slug, self.group.slug)

    def test_posts_profile_show_correct_context(self):
        """На странице группы только посты этой группы"""
        response = self.authorized_client.get(reverse(
            'posts:profile', args=(self.user.username,)))
        posts_set = response.context['page_obj']
        for post in posts_set:
            with self.subTest(post=post):
                self.assertEqual(post.author.username, self.user.username)

    def test_posts_detail_post_show_correct_context(self):
        """Страница поста содержит правильный пост"""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', args=(self.post.id,)))
        posts_from_page = response.context['post']
        self.assertEqual(posts_from_page.id, self.post.id)

    def test_posts_create_post_correct_context(self):
        """Форма создания поста корректна"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_edit_post_correct_context(self):
        """Форма редактированя поста корректна"""
        response = self.authorized_client.get(reverse('posts:post_edit',
                                                      args=(self.post.id,)))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        editable_post_id = response.context.get('post_id')
        self.assertEqual(editable_post_id, self.post.id)

    def test_posts_new_post_with_group_created(self):
        """Новый пост с группой размещен правильно"""
        adress_list = [
            reverse('posts:index'),
            reverse('posts:group_list', args=(self.group.slug,)),
            reverse('posts:profile', args=(self.user.username,)),
        ]
        group_set = Group.objects.exclude(slug=self.post.group.slug)
        for group in group_set:
            with self.subTest(group=group):
                response = self.client.get(reverse(
                    'posts:group_list', args=(self.group.slug,)
                )
                )
                self.assertNotIn(self.post.pk, response.context.get(
                    'page_obj').object_list)

        for adress in adress_list:
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(
                    self.post.pk, response.context.get('page_obj')[0].pk)
