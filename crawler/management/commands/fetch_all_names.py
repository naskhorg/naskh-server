import requests
import logging

from bs4 import BeautifulSoup
from crawler.models import NameEntity
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "Crawl quranic names website"

    TOTAL_PAGES = 315

    BASE_URL = "https://quranicnames.com/all-baby-names/page"

    def add_arguments(self, parser) -> None:
        return super().add_arguments(parser)

    def fetch(self, page_number):
        try:
            page = f"{self.BASE_URL}/{page_number}/"
            page_content = requests.get(page).text
            soup = BeautifulSoup(page_content, "html.parser")
            posts = soup.select('#catsdiv > div[id^="post-"]')
            for post in posts:
                anchor = post.find("a")
                category = anchor.get("class")[0]
                link = anchor.get("href")
                name = anchor.select_one(
                    ".entry-title-area h2.entry-title"
                ).text.strip()
                instance = NameEntity.objects.get_or_create(
                    name=name,
                    link=link,
                    category=category,
                )
                logger.info("Successfully created new post: %s", instance)
        except Exception as e:
            logger.info("Error fetching the page: %s", str(e))

    def handle(self, *args, **kwargs):
        for page_number in range(self.TOTAL_PAGES):
            self.fetch(page_number)
