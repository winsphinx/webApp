from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^bar/$', views.ChartView.as_view()),
    url(r'^index/$', views.IndexView.as_view()),
    url(r'^map/$', views.MapView.as_view()),
]
