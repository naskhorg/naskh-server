from concurrent.futures import ThreadPoolExecutor
from django.core.management.base import BaseCommand
from crawler.models import NameEntity


class Command(BaseCommand):

    def clean_description(self, name):
        updated = NameEntity.objects.get(id=name.id)
        short_meaning = updated.short_meaning
        if short_meaning and "Meaning:" in short_meaning:
            short_meaning = short_meaning.replace("Meaning:", "")
            updated.short_meaning = short_meaning
            updated.save()

    def handle(self, *args, **options):
        names = NameEntity.objects.all()
        with ThreadPoolExecutor(max_workers=20) as executor:
            list(executor.map(self.clean_description, names))
