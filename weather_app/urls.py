from django.urls import path
from . import views

urlpatterns = [
    path('', views.weather_home, name='home'),  # Ensure 'home' is named correctly
    path('food/', views.food_recommendations, name='food_recommendations'),
    path('clothing/', views.clothing_recommendations, name='clothing_recommendations'),

]