import requests

from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand
from crawler.models import NameEntity


class Command(BaseCommand):

    help = "Crawl name description from quranic names website"

    def build_entity_json(self, html):
        parsed_data = {
            "short_meaning": None,
            "arabic_name": None,
            "quranic_nature": None,
            "alternate_spellings": [],
            "root_link": None,
            "root_name": None,
        }
        # 1. Find div with class "entry-content"
        entry_content_div = html.find("div", class_="entry-content")
        if entry_content_div:
            # 2. Within "entry-content", find the div with class "artwork-meta-div"
            artwork_meta_div = entry_content_div.find("div", class_="artwork-meta-div")
            if artwork_meta_div:
                # Fetch tbody and its td for short_meaning
                short_meaning_td = (
                    artwork_meta_div.find("tbody").find("td")
                    if artwork_meta_div.find("tbody")
                    else None
                )
                parsed_data["short_meaning"] = (
                    short_meaning_td.get_text(strip=True) if short_meaning_td else None
                )

            # 3. Get arabic_name from first tr with class "tr1"
            tr1 = (
                artwork_meta_div.find("tr", class_="tr1") if artwork_meta_div else None
            )
            arabic_name_td = tr1.find("td") if tr1 else None
            parsed_data["arabic_name"] = (
                arabic_name_td.get_text(strip=True) if arabic_name_td else None
            )

            # 4. Get quranic_nature from second tr with class "tr2"
            tr2_list = (
                artwork_meta_div.find_all("tr", class_="tr2")
                if artwork_meta_div
                else []
            )
            if len(tr2_list) > 0:
                quranic_nature_td = tr2_list[0].find("td")
                parsed_data["quranic_nature"] = (
                    quranic_nature_td.get_text(strip=True)
                    if quranic_nature_td
                    else None
                )

                # 5. Get alternate spellings from spans in the second tr with class "tr2"
                alternate_spellings_spans = tr2_list[0].find_all("span")
                parsed_data["alternate_spellings"] = [
                    span.get_text(strip=True) for span in alternate_spellings_spans
                ]

            # 6. Get root_link and root_name from second tr with class "tr2" and id "root-info"
            root_info_tr = (
                artwork_meta_div.find("tr", class_="tr2", id="root-info")
                if artwork_meta_div
                else None
            )
            if root_info_tr:
                root_td = root_info_tr.find("td")
                root_a = root_td.find("a") if root_td else None
                if root_a:
                    parsed_data["root_link"] = root_a["href"]
                    parsed_data["root_name"] = root_a.get_text(strip=True)

            return parsed_data

    def handle(self, *args, **options):
        names = NameEntity.objects.filter(link="https://quranicnames.com/zaida/")
        for name in names:
            body = requests.get(name.link).text
            html = BeautifulSoup(body, "html.parser")
            response = self.build_entity_json(html)
            print(response)
