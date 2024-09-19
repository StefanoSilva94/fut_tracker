from . import views
from django.urls import path


urlpatterns = [
    path('sign_up/', views.login, name='sign_up'),
    path('login/', views.login, name='login'),
    # path('password_reset/', views.password_reset, name='password_reset')
]



