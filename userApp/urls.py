from django.urls import path

from . import views

app_name = 'userApp'
urlpatterns = [
    path('', views.index_view, name='index'),
]
