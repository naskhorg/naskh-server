from django.contrib import admin
from django.urls import path

from ninja import NinjaAPI
from crawler.api import router

api = NinjaAPI()

api.add_router("names/", router)


urlpatterns = [path("admin/", admin.site.urls), path("api/", api.urls)]
