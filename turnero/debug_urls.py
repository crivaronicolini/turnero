from django.urls import path
from .debug_views import url_index

urlpatterns = [
    path("url-index/", url_index, name="url_index"),
]
