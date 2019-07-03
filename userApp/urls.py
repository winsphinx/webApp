from django.urls import path

from . import views

app_name = 'userApp'
urlpatterns = [
    path('', views.main_view, name='main'),
    path('maps', views.users_maps_view, name='maps'),
    path('days', views.users_days_view, name='days'),
]
