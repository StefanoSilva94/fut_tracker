from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
import json


def getting_started(request):
    return render(request, 'info_pages/about.html')
   
    
def privacy_policy(request):
    return render(request, 'info_pages/about.html')