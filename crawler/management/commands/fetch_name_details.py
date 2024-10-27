import requests

from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from crawler.models import NameEntity


class Command(BaseCommand):

    help = "Crawl name description from quranic names website"

    def get_details(self, html):
        entity_json = {}
        entry_content_div = html.find("div", class_="entry-content")
        artwork_meta_div = entry_content_div.find("div", id="artwork-meta-div")
        short_meaning_td = artwork_meta_div.find("tbody").find("td")
        entity_json["short_meaning"] = short_meaning_td.contents[0].strip()
        entity_json["arabic_name"] = artwork_meta_div.find(
            "td", class_="arspelling"
        ).get_text(strip=True)
        tr2_list = artwork_meta_div.find_all("tr", class_="tr2")
        if len(tr2_list) > 0:
            entity_json["quranic_nature"] = tr2_list[1].find("td").get_text(strip=True)
            entity_json["alternate_spellings"] = [
                {span.get_text(strip=True): span.find("a")["href"]}
                for span in tr2_list[2].find_all("span")
            ]
        root_a = (
            artwork_meta_div.find("tr", class_="tr2", id="root-info")
            .find("td")
            .find("a")
        )
        root_list = (
            artwork_meta_div.find("tr", class_="tr2", id="root-info")
            .find("td")
            .find("div")
            .find_all("a")
        )
        entity_json["root_link"] = root_a["href"]
        entity_json["root_type"] = root_a.get_text(strip=True)
        entity_json["root_list"] = [
            {root_obj.text: root_obj["href"]} for root_obj in root_list
        ]
        entity_json['description'] =
        return entity_json

    def handle(self, *args, **options):
        names = NameEntity.objects.all()
        for name in names:
            print(name)
            body = requests.get(name.link).text
            html = BeautifulSoup(body, "html.parser")
            details = self.get_details(html)
            instance = NameEntity.objects.get(id=name.id)
            instance.details = details
            instance.save()
