from django.shortcuts import render
from django.db import connection


def home(request):
    with connection.cursor() as cursor:
        
        
        cursor.execute("SELECT COUNT(DISTINCT(pack_id)) FROM packed_items")
        total_packs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT(pack_id)) FROM player_picks")
        total_picks = cursor.fetchone()[0]
  
    return render(request, 'dashboards/home.html', 
                  {'total_packs': total_packs,
                   'total_picks': total_picks
                   })