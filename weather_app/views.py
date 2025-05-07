from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from .models import SearchHistory
import requests
import os
from dotenv import load_dotenv

# Load .env
dotenv_path = os.path.join(os.path.dirname(__file__), "../.env")
load_dotenv(dotenv_path)
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# ========== AUTH VIEWS ==========

def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'weather_app/signup.html', {'form': form})

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")  # Make sure 'home' is your weather page URL name
        else:
            if not User.objects.filter(username=username).exists():
                error = "User does not exist. Please sign up first."
            else:
                error = "Incorrect password. Please try again."

    return render(request, "weather_app/login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect('login')

# ========== WEATHER LOGIC ==========

def get_weather_data(city):
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    response = requests.get(BASE_URL, params={"q": city, "appid": API_KEY, "units": "metric"})
    if response.status_code == 200:
        return response.json()
    return None

def get_forecast_data(city):
    BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"
    response = requests.get(BASE_URL, params={"q": city, "appid": API_KEY, "units": "metric"})
    if response.status_code == 200:
        forecast_list = response.json()["list"]
        daily_forecast = {}
        for entry in forecast_list:
            date = entry["dt_txt"].split(" ")[0]
            if date not in daily_forecast:
                weather_desc = entry["weather"][0]["description"].lower()
                if "clear" in weather_desc:
                    weather_emoji = "☀️"
                elif "cloud" in weather_desc:
                    weather_emoji = "☁️"
                elif "rain" in weather_desc:
                    weather_emoji = "🌧️"
                elif "thunderstorm" in weather_desc:
                    weather_emoji = "⛈️"
                elif "snow" in weather_desc:
                    weather_emoji = "❄️"
                elif "mist" in weather_desc or "fog" in weather_desc:
                    weather_emoji = "🌫️"
                elif "drizzle" in weather_desc:
                    weather_emoji = "🌦️"
                elif "haze" in weather_desc:
                    weather_emoji = "🌁"
                else:
                    weather_emoji = "🌍"
                entry["weather_emoji"] = weather_emoji
                daily_forecast[date] = entry
        return list(daily_forecast.values())[:5]
    return None

# ========== MAIN WEATHER VIEW ==========

@login_required
def weather_home(request):
    city_name = None
    weather_data = None
    forecast_data = None
    weather_emoji = ""
    search_history = []

    if request.method == "POST":
        city_name = request.POST["city_name"]
        weather_data = get_weather_data(city_name)
        forecast_data = get_forecast_data(city_name)

        if not weather_data:
            return render(request, "weather_app/home.html", {"error_message": "City not found"})

        # Save to history
        SearchHistory.objects.create(user=request.user, city=city_name)

        weather_desc = weather_data["weather"][0]["description"].lower()
        if "clear" in weather_desc:
            weather_emoji = "☀️"
        elif "cloud" in weather_desc:
            weather_emoji = "☁️"
        elif "rain" in weather_desc:
            weather_emoji = "🌧️"
        elif "thunderstorm" in weather_desc:
            weather_emoji = "⛈️"
        elif "snow" in weather_desc:
            weather_emoji = "❄️"
        elif "mist" in weather_desc or "fog" in weather_desc:
            weather_emoji = "🌫️"
        elif "drizzle" in weather_desc:
            weather_emoji = "🌦️"
        elif "haze" in weather_desc:
            weather_emoji = "🌁"
        else:
            weather_emoji = "🌍"

    # Fetch last 5 searches
    search_history = SearchHistory.objects.filter(user=request.user).order_by('-searched_at')[:5]

    return render(request, "weather_app/home.html", {
        "city_name": city_name,
        "temp": weather_data["main"]["temp"] if weather_data else None,
        "humidity": weather_data["main"]["humidity"] if weather_data else None,
        "weather_description": f"{weather_data['weather'][0]['description'].capitalize()} {weather_emoji}" if weather_data else None,
        "forecast": forecast_data,
        "search_history": search_history
    })

# ========== FOOD RECOMMENDATION ==========

@login_required
def food_recommendations(request):
    city_name = request.GET.get("city_name")
    if not city_name:
        return redirect("home")
    weather_data = get_weather_data(city_name)
    if not weather_data:
        return render(request, "weather_app/food.html", {"error_message": "Weather data not available."})
    temp = weather_data["main"]["temp"]
    weather_description = weather_data["weather"][0]["description"].lower()
    if "rain" in weather_description:
        food_list = ["Pakoras 🥟", "Tea ☕", "Hot Corn 🌽"]
    elif temp < 20:
        food_list = ["Soup 🍜", "Hot Chocolate 🍫", "Warm Rice 🍚"]
    else:
        food_list = ["Ice Cream 🍦", "Cold Coffee ☕", "Fresh Juices 🥤"]
    return render(request, "weather_app/food.html", {
        "city_name": city_name,
        "food_list": food_list,
        "temp": temp,
        "weather_description": weather_description
    })

# ========== CLOTHING RECOMMENDATION ==========

@login_required
def clothing_recommendations(request):
    city_name = request.GET.get("city_name")
    if not city_name:
        return redirect("home")
    weather_data = get_weather_data(city_name)
    if not weather_data:
        return render(request, "weather_app/clothing.html", {"error_message": "Weather data not available."})
    temp = weather_data["main"]["temp"]
    weather_description = weather_data["weather"][0]["description"].lower()
    if "rain" in weather_description:
        clothing_list = ["Raincoat ☔", "Umbrella 🌂", "Waterproof Shoes 👞"]
    elif temp < 20:
        clothing_list = ["Jacket 🧥", "Sweater 🧣", "Boots 🥾"]
    else:
        clothing_list = ["T-Shirts 👕", "Shorts 🩳", "Sunglasses 🕶"]
    return render(request, "weather_app/clothing.html", {
        "city_name": city_name,
        "clothing_list": clothing_list,
        "temp": temp,
        "weather_description": weather_description
    })
