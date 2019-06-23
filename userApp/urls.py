from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view()),
    path('bar/', views.ChartView.as_view()),
    path('index/', views.IndexView.as_view()),
    path('map/', views.MapView.as_view()),
]
