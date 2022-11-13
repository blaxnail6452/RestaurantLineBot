from django.urls import path
from . import views
 
urlpatterns = [
    path('callback', views.callback),
    path('random_recommend', views.random_recommend),
]