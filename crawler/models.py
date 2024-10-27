from django.db import models


class NameEntity(models.Model):
    name = models.CharField(max_length=255)
    link = models.URLField()
    category = models.CharField(max_length=255)
    # entity_json = models.TextField(default="")

    def __str__(self):
        return f"{self.name}:{self.link}:{self.category}"
