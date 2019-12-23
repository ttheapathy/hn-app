from operator import itemgetter

from django.test import TestCase, Client
from django.conf import settings

from rest_framework import status

from .models import Post
from .views import PostSerializer


class PostTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        posts = [Post(story_id=i + 1, title='Title {}'.format(i + 1), url='https://example.com/{}'.format(i + 1)) for i in range(30)]
        Post.objects.bulk_create(posts, ignore_conflicts=False)

    def test_default_posts_count(self):
        response = self.client.get('/posts')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), settings.REST_FRAMEWORK.get('PAGE_SIZE'))

    def test_serializer_posts_count(self):
        response = self.client.get('/posts')
        posts = Post.objects.all()[:settings.REST_FRAMEWORK.get('PAGE_SIZE')]
        serializer = PostSerializer(posts, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_single_post(self):
        post = Post.objects.get(story_id=5)
        self.assertEqual(post.title, 'Title 5')

    def test_order(self):
        response = self.client.get('/posts?order=id')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), settings.REST_FRAMEWORK.get('PAGE_SIZE'))
        self.assertSequenceEqual(list(map(itemgetter('title'), response.json())), ['Title 1', 'Title 2', 'Title 3', 'Title 4', 'Title 5'])

        response = self.client.get('/posts?order=-id')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), settings.REST_FRAMEWORK.get('PAGE_SIZE'))
        self.assertSequenceEqual(list(map(itemgetter('title'), response.json())), ['Title 30', 'Title 29', 'Title 28', 'Title 27', 'Title 26'])

        response = self.client.get('/posts?order=abc')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_limit(self):
        response = self.client.get('/posts?limit=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)
        self.assertSequenceEqual(list(map(itemgetter('title'), response.json())), ['Title 1', 'Title 2'])

        response = self.client.get('/posts?limit=abc')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get('/posts?limit={}'.format(-10))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get('/posts?limit={}'.format(settings.MAX_PAGE_SIZE + 10))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_offset(self):
        response = self.client.get('/posts?offset=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), settings.REST_FRAMEWORK.get('PAGE_SIZE'))
        self.assertSequenceEqual(list(map(itemgetter('title'), response.json())), ['Title 3', 'Title 4', 'Title 5', 'Title 6', 'Title 7'])

        response = self.client.get('/posts?offset=abcde')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get('/posts?offset={}'.format(-10))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_multiple_params(self):
        response = self.client.get('/posts?limit=2&offset=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)
        self.assertSequenceEqual(list(map(itemgetter('title'), response.json())), ['Title 3', 'Title 4', ])

        response = self.client.get('/posts?order=-id&limit=2&offset=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)
        self.assertSequenceEqual(list(map(itemgetter('title'), response.json())), ['Title 28', 'Title 27', ])

    def tearDown(self):
        Post.objects.all().delete()


class FetchPostsTestCase(TestCase):

    def test_fetch_posts(self):
        self.assertEqual(Post.objects.count(), 0)
        self.client.get('/posts/_fetch')
        self.assertEqual(Post.objects.count(), 30)

    def tearDown(self):
        Post.objects.all().delete()
