from django.contrib.auth.views import LoginView
from django.urls import path

from . import views

app_name = 'adminApp'
urlpatterns = [
    path('login/', LoginView.as_view(template_name='login.html'),
         name='login'),
    # path('bar/', views.bar_view),
    # path('', views.IndexView.as_view()),
    # path('bar/', views.ChartView.as_view()),
    # path('index/', views.IndexView.as_view()),
    # path('map/', views.MapView.as_view()),
]
