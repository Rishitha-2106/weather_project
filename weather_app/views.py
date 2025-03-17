from django.shortcuts import redirect, render
import requests
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file
API_KEY = os.getenv("OPENWEATHER_API_KEY")  # Retrieve the API key securely


# Function to get weather data
def get_weather_data(city):
    API_KEY = os.getenv("OPENWEATHER_API_KEY")    
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    response = requests.get(BASE_URL, params={"q": city, "appid": API_KEY, "units": "metric"})
    if response.status_code == 200:
        return response.json()
    return None

# Function to get 5-day forecast
def get_forecast_data(city):
    API_KEY = os.getenv("OPENWEATHER_API_KEY")  # Retrieve the API key securely
    BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"
    response = requests.get(BASE_URL, params={"q": city, "appid": API_KEY, "units": "metric"})
    if response.status_code == 200:
        forecast_list = response.json()["list"]
        # Extract only one forecast per day (choosing data at 12:00 PM)
        daily_forecast = {}
        for entry in forecast_list:
            date = entry["dt_txt"].split(" ")[0]  # Extract only the date (YYYY-MM-DD)
            if date not in daily_forecast:  # Store only one entry per day
                weather_desc = entry["weather"][0]["description"].lower()
                # Assign emojis based on weather description
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
                # Add emoji to forecast data
                entry["weather_emoji"] = weather_emoji
                daily_forecast[date] = entry
        return list(daily_forecast.values())[:5]  # Return next 5 days
    return None

# Home page view (Displays Weather + Forecast)
def weather_home(request):
    city_name = None
    weather_data = None
    forecast_data = None
    weather_emoji = ""
    if request.method == "POST":
        city_name = request.POST["city_name"]
        weather_data = get_weather_data(city_name)
        forecast_data = get_forecast_data(city_name)
        if not weather_data:
            return render(request, "weather_app/home.html", {"error_message": "City not found"})
        # Assign emojis based on weather description
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
    return render(request, "weather_app/home.html", {
        "city_name": city_name,
        "temp": weather_data["main"]["temp"] if weather_data else None,
        "humidity": weather_data["main"]["humidity"] if weather_data else None,
        "weather_description": f"{weather_data['weather'][0]['description'].capitalize()} {weather_emoji}" if weather_data else None,
        "forecast": forecast_data,
    })

# Food recommendations page (Only accessible if city is provided)
def food_recommendations(request):
    city_name = request.GET.get("city_name")
    if not city_name:
        return redirect("home")  # Redirect to home if no city
    weather_data = get_weather_data(city_name)
    if not weather_data:
        return render(request, "weather_app/food.html", {"error_message": "Weather data not available."})
    temp = weather_data["main"]["temp"]
    weather_description = weather_data["weather"][0]["description"].lower()
    # Food recommendation logic based on temperature
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

# Clothing recommendations page (Only accessible if city is provided)
def clothing_recommendations(request):
    city_name = request.GET.get("city_name")
    if not city_name:
        return redirect("home")  # Redirect to home if no city
    weather_data = get_weather_data(city_name)
    if not weather_data:
        return render(request, "weather_app/clothing.html", {"error_message": "Weather data not available."})
    temp = weather_data["main"]["temp"]
    weather_description = weather_data["weather"][0]["description"].lower()
    # Clothing recommendation logic based on temperature
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