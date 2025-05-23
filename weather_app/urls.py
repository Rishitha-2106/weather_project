from django.urls import path
from . import views

urlpatterns = [
    path('', views.weather_home, name='home'),  # Ensure 'home' is named correctly
    path('food/', views.food_recommendations, name='food_recommendations'),
    path('clothing/', views.clothing_recommendations, name='clothing_recommendations'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.user_profile, name='profile'),  # Add profile URL
    path('history/', views.search_history, name='search_history'),


]