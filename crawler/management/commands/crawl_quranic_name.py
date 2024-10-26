import requests
from models import Post
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

TOTAL_PAGES = 315

BASE_URL = "https://quranicnames.com/all-baby-names/page/"


class Command(BaseCommand):
    
    help = 'Crawl quranic names website'
    
    def add_arguments(self, parser) -> None:
        return super().add_arguments(parser)
    
    def fetch_and_create(self, page_content):
        try:
            soup = BeautifulSoup(page_content, 'html.parser')
            posts = soup.select('#catsdiv > div[id^="post-"]')
            for post in posts:
                anchor = post.find('a')
                category = anchor.get('class')
                link = anchor.get('href')
                name = anchor.select_one('.entry-title-area h2.entry-title').text.strip()
                instance = Post.objects.create(
                    name=name,
                    link=link,
                    category=category,
                )
                print(f'Successfully created post: {instance}')
        except Exception as e:
            print(f"Error fetching the page: {e}")
    
    def handle(self, *args, **kwargs):
        for i in range(TOTAL_PAGES):
            url = f'{BASE_URL}/{i}/'
            page = requests.get(url)
            self.fetch_and_create(page.body)