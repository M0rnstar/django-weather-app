import requests
from django.shortcuts import render
from django.http import JsonResponse
from .models import SearchLog

def home_view(request):
    weather_data = None
    forecast_data = None
    error = None
    city = request.GET.get("city")

    if city:
        # Сохраняем/обновляем базу
        log, created = SearchLog.objects.get_or_create(city__iexact=city, defaults={"city": city})
        if not created:
            log.count += 1
            log.save()

        request.session["last_city"] = city

        # История поиска
        search_history = request.session.get("search_history", [])
        if city not in search_history:
            search_history.append(city)
            request.session["search_history"] = search_history

        # Геокодинг
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {"name": city, "count": 1, "language": "ru", "format": "json"}
        geo_response = requests.get(geo_url, params=geo_params)

        if geo_response.status_code == 200:
            geo_data = geo_response.json()
            if "results" in geo_data:
                lat = geo_data["results"][0]["latitude"]
                lon = geo_data["results"][0]["longitude"]

                # Прогноз
                weather_url = "https://api.open-meteo.com/v1/forecast"
                weather_params = {
                    "latitude": lat,
                    "longitude": lon,
                    "current_weather": True,
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                    "timezone": "auto",
                }
                weather_response = requests.get(weather_url, params=weather_params)

                if weather_response.status_code == 200:
                    weather_json = weather_response.json()
                    weather_data = weather_json.get("current_weather")
                    
                    forecast_data = []
                    if "daily" in weather_json:
                        daily = weather_json["daily"]
                        for i in range(len(daily["time"])):
                            forecast_data.append({
                                "date": daily["time"][i],
                                "temp_min": daily["temperature_2m_min"][i],
                                "temp_max": daily["temperature_2m_max"][i],
                                "precip": daily["precipitation_probability_max"][i],
                            })
                else:
                    error = "Ошибка при получении прогноза погоды."
            else:
                error = "Город не найден."
        else:
            error = "Ошибка при запросе геолокации."

    last_city = request.session.get("last_city") if not city else None
    search_history = request.session.get("search_history", [])

    return render(request, "home.html", {
        "weather": weather_data,
        "forecast": forecast_data,
        "error": error,
        "last_city": last_city,
        "history": search_history,
    })

def stats_api(request):
    data = {
        log.city: log.count
        for log in SearchLog.objects.all().order_by("-count")
    }
    return JsonResponse(data, json_dumps_params={'ensure_ascii': False})


def autocomplete_city(request):
    query = request.GET.get("q")
    if query:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {"name": query, "count": 5, "language": "ru", "format": "json"}
        response = requests.get(geo_url, params=geo_params)

        if response.status_code == 200:
            data = response.json()
            results = [res["name"] for res in data.get("results", [])]
            return JsonResponse({"results": results}, json_dumps_params={'ensure_ascii': False})

    return JsonResponse({"results": []})

