from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/get_pack_data/', views.get_pack_data, name='get_pack_data'),
    path('chart/', views.chart_view, name='chart_view'),

]
