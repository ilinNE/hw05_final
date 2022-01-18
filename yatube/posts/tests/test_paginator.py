from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='tester')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Описание тестовой группы'
        )
        for i in range(13):
            Post.objects.create(
                text='Тестовый текст c текстом',
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        self.client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        """Паджинатор на первой странице работает корректно"""
        adress_list = [
            reverse('posts:index'),
            reverse('posts:group_list', args=(self.group.slug,)),
            reverse('posts:profile', args=(self.user.username,)),
        ]
        posts_in_first_page = settings.POST_PER_PAGE
        for adress in adress_list:
            with self.subTest(adress=adress):
                response = self.client.get(adress)
                self.assertEqual(len(response.context['page_obj']),
                                 posts_in_first_page
                                 )

    def test_second_page_contains_ten_records(self):
        """Паджинатор на второй странице работает корректно"""
        adress_list = [
            reverse('posts:index'),
            reverse('posts:group_list', args=(self.group.slug,)),
            reverse('posts:profile', args=(self.user.username,)),
        ]
        post_count = Post.objects.count()
        if post_count - settings.POST_PER_PAGE > settings.POST_PER_PAGE:
            posts_in_sec_page = settings.POST_PER_PAGE
        else:
            posts_in_sec_page = post_count - settings.POST_PER_PAGE
        for adress in adress_list:
            with self.subTest(adress=adress):
                response = self.client.get(adress + '?page=2')
                self.assertEqual(len(response.context['page_obj']),
                                 posts_in_sec_page
                                 )
