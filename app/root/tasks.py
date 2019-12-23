import requests
import bs4

from django.conf import settings
from hn.celery import app
from .models import Post


@app.task(default_retry_delay=30, max_retries=1, time_limit=60, ignore_result=True)
def fetch_posts():
    response = requests.get(settings.HACKER_URL)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    posts = []

    for element in soup.find_all(attrs={'class': 'athing'}):
        posts.append(Post(
            story_id=element.attrs['id'],
            title=element.select_one('td.title a.storylink').string,
            url=element.select_one('td.title a.storylink')['href'])
        )
    Post.objects.bulk_create(posts, ignore_conflicts=True)
