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
        entity_json["description"] = (
            entry_content_div.find("div", id="name_details")
            .find("p")
            .get_text(strip=True)
        )
        short_meaning_node = artwork_meta_div.find("tbody").find("tr", class_="tr2")
        if short_meaning_node:
            short_meaning_td = short_meaning_node.find("td")
            if short_meaning_td:
                entity_json["short_meaning"] = short_meaning_td.get_text(strip=True)
        tr2_list = artwork_meta_div.find_all("tr", class_="tr2")
        if len(tr2_list) > 1:
            entity_json["quranic_nature"] = tr2_list[1].find("td").get_text(strip=True)
            if len(tr2_list) > 2:
                entity_json["alternate_spellings"] = {
                    span.get_text(strip=True): span.find("a")["href"]
                    for span in tr2_list[2].find_all("span")
                }

        root_info = artwork_meta_div.find("tr", class_="tr2", id="root-info")
        if root_info:
            root_info_node = root_info.find("td")
            if root_info_node:
                root_a = root_info_node.find("a")
                entity_json["root_link"] = root_a["href"]
                entity_json["root_type"] = root_a.get_text(strip=True)
                root_info_div = root_info_node.find("div")
                if root_info_div:
                    root_links = root_info_div.find_all("a")
                    entity_json["similar_root_names"] = {
                        root_obj.text: root_obj["href"] for root_obj in root_links
                    }
        entity_json["verses"] = []
        name_details = entry_content_div.find("div", id="name_details")
        if name_details:
            for quote in name_details.find_all("p"):
                entity_json["verses"].append(quote.get_text(strip=True))
        return entity_json

    def handle(self, *args, **options):
        names = NameEntity.objects.all()
        for name in names:
            print(name.link)
            body = requests.get(name.link).text
            html = BeautifulSoup(body, "html.parser")
            details = self.get_details(html)
            updated = NameEntity.objects.get(link=name.link)
            similar_root_names = details.get("similar_root_names", {})
            for similar_name, similar_name_link in similar_root_names.items():
                similar_name = similar_name if similar_name else ""
                s_instance, s_created = NameEntity.objects.get_or_create(
                    name=similar_name, link=similar_name_link
                )
                updated.similar_root_names.add(s_instance)

            alternate_spellings = details.get("alternate_spellings", {})
            for alt_name, alt_link in alternate_spellings.items():
                alt_name = alt_name if alt_name else ""
                alt_instance, created = NameEntity.objects.get_or_create(
                    name=alt_name, link=alt_link
                )
                updated.alternative_spellings.add(alt_instance)

            updated.details = details
            updated.save()
