from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Follow, Post


User = get_user_model()


class PostsFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create_user(username='follower')
        cls.author = User.objects.create_user(username='author')
        cls.non_follower = User.objects.create_user(username='non_follower')

    def setUp(self):
        self.client.force_login(self.follower)

    def test_following_possible(self):
        self.assertFalse(Follow.objects.filter(
            user=self.follower,
            author=self.author
        ))
        self.client.get(reverse(
            'posts:profile_follow',
            args={self.author.username}
        ))
        self.assertTrue(Follow.objects.filter(
            user=self.follower,
            author=self.author
        ))

    def test_unfollowing_possible(self):
        Follow.objects.create(
            user=self.follower,
            author=self.author
        )
        self.assertTrue(Follow.objects.filter(
            user=self.follower,
            author=self.author
        ))
        self.client.get(reverse(
            'posts:profile_unfollow',
            args={self.author.username}
        ))
        self.assertFalse(Follow.objects.filter(
            user=self.follower,
            author=self.author
        ))

    def test_new_post_show_for_followers_only(self):
        non_follower_client = Client()
        non_follower_client.force_login(self.non_follower)
        Follow.objects.create(
            user=self.follower,
            author=self.author
        )
        new_post = Post.objects.create(
            author=self.author,
            text='Текст нового поста'

        )
        follower_response = self.client.get(reverse('posts:follow_index'))
        non_follower_response = non_follower_client.get(
            reverse('posts:follow_index')
        )
        self.assertIn(new_post, follower_response.context['page_obj'])
        self.assertNotIn(new_post, non_follower_response.context['page_obj'])
