from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

from crawler.models import NameEntity


class Command(BaseCommand):

    help = "Crawl name description from quranic names website"

    def parse_details(self, name):
        entity_json = dict()
        entity_json["verses"] = []
        entity_json["category"] = name.category or ""
        entity_json["description"] = ""
        entity_json["short_meaning"] = ""
        entity_json["quranic_nature"] = ""
        entity_json["similar_root_names"] = {}
        entity_json["alternate_spellings"] = {}
        body = requests.get(name.link).text
        html = BeautifulSoup(body, "html.parser")
        self.get_details(html, entity_json)
        self.parse_content(html, entity_json)
        self.parse_staff_answers(html, entity_json)
        self.update_details_in_db(entity_json, name)

    def set_arabic_spelling(self, artwork_meta_div, entity_json):
        entity_json["arabic_name"] = ""
        if not artwork_meta_div or not artwork_meta_div.find("tbody"):
            return
        for tr in artwork_meta_div.find("tbody").find_all("tr", class_="tr1"):
            key = tr.find("th").contents[0].strip()
            if "Arabic Spelling" in key:
                entity_json["arabic_name"] = tr.find(
                    "td", class_="arspelling"
                ).get_text(strip=True)

    def get_details(self, html, entity_json):
        entry_content_div = html.find("div", class_="entry-content")
        if not entry_content_div:
            return entity_json
        name_details = entry_content_div.find("div", id="name_details")
        if name_details:
            entity_json["description"] = name_details.find("p").get_text(strip=True)
            block_quotes = name_details.find("blockquote")
            entity_json["verses"] = []
            if block_quotes:
                verses = [p.get_text(strip=True) for p in block_quotes.find_all("p")]
                entity_json["verses"].extend(verses)
        artwork_meta_div = entry_content_div.find("div", id="artwork-meta-div")
        if not artwork_meta_div or not artwork_meta_div.find("tbody"):
            return entity_json
        self.set_arabic_spelling(artwork_meta_div, entity_json)
        for tr in artwork_meta_div.find("tbody").find_all("tr", class_="tr2"):
            tr2_key = tr.find("th").contents[0].strip()
            if tr2_key == "Quranic Nature":
                entity_json["quranic_nature"] = tr.find("td").get_text(strip=True)
            elif "Short" in tr2_key:
                td = tr.find("td")
                result = ""
                try:
                    if td and td.contents:
                        result = td.contents[0].strip()
                except Exception:
                    pass
                entity_json["short_meaning"] = result
            elif "Alternate spellings" in tr2_key:
                entity_json["alternate_spellings"] = {
                    span.get_text(strip=True): span.find("a")["href"]
                    for span in tr.find_all("span")
                }
            elif tr2_key == "Quranic Root":
                root_info_node = tr.find("td")
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

    def parse_content(self, html, entity_json):
        try:
            category = html.find("h3").get_text(strip=True)
            short_meaning = (
                html.find("h4").get_text(strip=True) if html.find("h4") else ""
            )
            all_ps = html.find(id="variant-div").find_all("p")
            description = (
                all_ps[2].get_text(strip=True)
                if len(all_ps) > 2
                else all_ps[0].get_text(strip=True)
            )
            verses = [
                blockquote.get_text(strip=True)
                for blockquote in html.find_all("blockquote")
            ]
            if not entity_json["category"]:
                entity_json["category"] = category.split(" ")[-1]
            if not entity_json["short_meaning"]:
                entity_json["short_meaning"] = short_meaning
            if not entity_json["description"]:
                entity_json["description"] = description
            if not entity_json["verses"]:
                entity_json["verses"] = verses
        except Exception:
            pass

    def parse_staff_answers(self, html, entity_json):
        try:
            description = (
                html.find("div", class_="entry-content")
                .find_all("p")[1]
                .get_text(strip=True)
            )
            if not entity_json["description"]:
                entity_json["description"] = description
        except Exception:
            pass

    def update_details_in_db(self, details, name):
        updated = NameEntity.objects.get(id=name.id)
        updated.category = details.get("category", "")
        updated.description = details.get("description", "")
        updated.short_meaning = details.get("short_meaning", "")
        updated.arabic_name = details.get("arabic_name", "")
        updated.quranic_nature = details.get("quranic_nature", "")
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

    def handle(self, *args, **options):
        names = NameEntity.objects.filter(
            description="",
        )
        with ThreadPoolExecutor(max_workers=20) as executor:
            list(executor.map(self.parse_details, names))
