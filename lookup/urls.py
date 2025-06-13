from django.urls import path
from . import views

urlpatterns=[
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('weather/', views.weather_result, name='weather_result'),
    path('compare/', views.compare_weather, name='compare_weather'),
    
]