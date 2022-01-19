from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post

User = get_user_model()


class PostsCacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.user = User.objects.create_user(username='testuser')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )

    def test_index_cached(self):
        """Страница индекс кешируется"""
        response = self.client.get(reverse('posts:index'))
        start_content = response.content
        self.post.delete()
        self.assertIn(self.post.text, response.content.decode())
        response = self.client.get(reverse('posts:index'))
        deleted_post_content = response.content
        self.assertIn(self.post.text, response.content.decode())
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        clear_cache_content = response.content
        self.assertNotIn(self.post.text, response.content.decode())
        self.assertEqual(start_content, deleted_post_content)
        self.assertNotEqual(start_content, clear_cache_content)
