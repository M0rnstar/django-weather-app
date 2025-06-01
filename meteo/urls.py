from django.urls import path
from .views import home_view, stats_api, autocomplete_city

urlpatterns = [
    path("home/", home_view, name="home"),
    path("api/stats/", stats_api, name="stats_api"),
    path("autocomplete/", autocomplete_city, name="autocomplete_city"),
]
