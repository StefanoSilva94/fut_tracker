from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('api/create-distribution-rating-chart/', views.create_distribution_rating_chart, name='create_distribution_rating_chart'),
    path('my-packs/', views.my_packs, name='my_packs'),
    ]

