from django.db import models

class Post(models.Model):
    name = models.Text()
    category = models.Text()
    link = models.Text()