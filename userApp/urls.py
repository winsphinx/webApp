from django.urls import include, path
from . import views

urlpatterns = [
    path('bar/', views.ChartView.as_view()),
    path('index/', views.IndexView.as_view()),
    path('map/', views.MapView.as_view()),
]
