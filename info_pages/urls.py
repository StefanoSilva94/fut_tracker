from django.urls import path
from . import views

urlpatterns = [
    path('getting-started/', views.getting_started, name='getting_started'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
]