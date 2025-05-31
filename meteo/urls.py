from django.urls import path
from .views import home_view, stats_api

urlpatterns = [
    path("home/", home_view, name="home"),
    path("api/stats/", stats_api, name="stats_api"),
]
