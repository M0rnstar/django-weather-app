from django.test import TestCase, Client
from django.urls import reverse
from .models import SearchLog

class WeatherAppTests(TestCase):
    def setUp(self):
        # Создание клиента, с помощью которого будет отправляться запрос
        self.client = Client()
        self.search_url = reverse("home")
        self.stats_url = reverse("stats_api")

    def test_homepage_loads(self):
        # Проверяет, что главная страница загружается корректно
        response = self.client.get(self.search_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")

    def test_stats_api_returns_json(self):
        # Проверяет, что API статистики возвращает корректный JSON
        SearchLog.objects.create(city="Москва", count=3)
        SearchLog.objects.create(city="Нальчик", count=1)

        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIn("Москва", response.json())
        self.assertEqual(response.json()["Москва"], 3)

    def test_city_search_adds_to_session_and_db(self):
        # Проверяет, что после ввода города он сохраняется в сессии и базе
        response = self.client.get(self.search_url, {"city": "Москва"})
        self.assertEqual(response.status_code, 200)

        session = self.client.session
        self.assertEqual(session.get("last_city"), "Москва")

        self.assertTrue(SearchLog.objects.filter(city="Москва").exists())
