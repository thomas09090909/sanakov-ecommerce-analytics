"""
Custom API Exporter
Collects weather metrics for multiple cities in Kazakhstan
"""

from prometheus_client import start_http_server, Gauge, Info
import requests
import time
from bisect import bisect_left

# --- METRICS ---
weather_temperature = Gauge('weather_temperature_celsius', 'Current temperature', ['city', 'country'])
weather_windspeed = Gauge('weather_windspeed_kmh', 'Current wind speed', ['city', 'country'])
weather_humidity = Gauge('weather_humidity_percent', 'Humidity', ['city', 'country'])
weather_pressure = Gauge('weather_pressure_hpa', 'Pressure', ['city', 'country'])
weather_cloudcover = Gauge('weather_cloudcover_percent', 'Cloud cover', ['city', 'country'])
weather_visibility = Gauge('weather_visibility_km', 'Visibility', ['city', 'country'])
weather_api_status = Gauge('weather_api_status', 'Weather API status (1=up, 0=down)')
weather_uv = Gauge('weather_uv_index', 'UV index', ['city', 'country'])
weather_precipitation = Gauge('weather_precipitation_mm', 'Precipitation', ['city', 'country'])

exporter_info = Info('custom_exporter', 'Custom metrics exporter info')

# --- CITIES ---
CITIES = [
    {'name': 'Astana', 'country': 'Kazakhstan', 'lat': 51.1694, 'lon': 71.4491},
    {'name': 'Almaty', 'country': 'Kazakhstan', 'lat': 43.2220, 'lon': 76.8512},
    {'name': 'Karaganda', 'country': 'Kazakhstan', 'lat': 49.8047, 'lon': 73.1094},
    {'name': 'Semey', 'country': 'Kazakhstan', 'lat': 50.4166, 'lon': 80.2329},
    {'name': 'Shymkent', 'country': 'Kazakhstan', 'lat': 42.3000, 'lon': 69.6000}
]

def get_nearest_index(times, target):
    pos = bisect_left(times, target)
    if pos == 0:
        return 0
    if pos == len(times):
        return len(times) - 1
    before = times[pos - 1]
    after = times[pos]
    return pos if abs(after > target) else pos - 1

def fetch_weather_for_city(city_data):
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': city_data['lat'],
            'longitude': city_data['lon'],
            'current_weather': 'true',
            'hourly': 'relativehumidity_2m,pressure_msl,cloudcover,visibility,uv_index,precipitation',
            'timezone': 'Asia/Almaty'
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        current = data['current_weather']
        city = city_data['name']
        country = city_data['country']

        weather_temperature.labels(city=city, country=country).set(current['temperature'])
        weather_windspeed.labels(city=city, country=country).set(current['windspeed'])

        time_list = data['hourly']['time']
        current_time = current['time']
        try:
            now_idx = time_list.index(current_time)
        except ValueError:
            now_idx = get_nearest_index(time_list, current_time)

        weather_humidity.labels(city=city, country=country).set(data['hourly']['relativehumidity_2m'][now_idx])
        weather_pressure.labels(city=city, country=country).set(data['hourly']['pressure_msl'][now_idx])
        weather_cloudcover.labels(city=city, country=country).set(data['hourly']['cloudcover'][now_idx])
        weather_visibility.labels(city=city, country=country).set(data['hourly']['visibility'][now_idx] / 1000)
        weather_uv.labels(city=city, country=country).set(data['hourly']['uv_index'][now_idx])
        weather_precipitation.labels(city=city, country=country).set(data['hourly']['precipitation'][now_idx])

        return True
    except Exception as e:
        print(f"Error fetching weather for {city_data['name']}: {e}")
        return False

def fetch_weather():
    success_count = 0
    for city in CITIES:
        if fetch_weather_for_city(city):
            success_count += 1
    weather_api_status.set(1 if success_count > 0 else 0)
    return success_count > 0

if __name__ == '__main__':
    exporter_info.info({'version': '1.3', 'author': 'Student', 'sources': 'weather'})
    start_http_server(8000)
    print("Custom Exporter running on port 8000")
    print(f"Monitoring cities: {', '.join([c['name'] for c in CITIES])}")

    while True:
        try:
            fetch_weather()
            print("Metrics updated for all cities")
        except KeyboardInterrupt:
            print("Stopping...")
            break
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(20)  # update frequency
