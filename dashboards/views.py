from django.shortcuts import render
from django.db import connection
from .charts.chart_utils import create_time_query_filter
from django.http import JsonResponse
from .charts import charts
import json


def home(request):
    with connection.cursor() as cursor:
        
        
        cursor.execute("SELECT COUNT(DISTINCT(pack_id)) FROM packed_items")
        total_packs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT(pack_id)) FROM player_picks")
        total_picks = cursor.fetchone()[0]
        
        cursor.execute("SELECT DISTINCT(pack_name) FROM packed_items")
        pack_names = cursor.fetchall()
        
        cursor.execute("SELECT DISTINCT(pack_name) FROM player_picks")
        pick_names = cursor.fetchall()
        
        # Flatten the list of tuples
        pack_names = [name[0] for name in pack_names] 
        pick_names = [name[0] for name in pick_names] 
  
    return render(request, 'dashboards/home.html', 
                  {'total_packs': total_packs,
                   'total_picks': total_picks,
                   'pack_names': pack_names,
                   'pick_names': pick_names,
                   })



def create_distribution_rating_chart(request):
    """
    Extracts the pack name and time filter from the request.
    Creates a ratingsDistributionsChart object
    
    """
    

    data = json.loads(request.body)
    pack = data.get('pack', 'all')  # Get pack selection
    time_filter = data.get('time', 'all_time') 
    if pack[0:4] == '1 of':
        pack_or_pick = 'pick'
    else:
        pack_or_pick = 'pack'
        
    ratings_dist_chart = charts.ratingsDistributionsChart(pack_or_pick, pack, time_filter)
    ratings_dist_chart.get_data()
    print(f"total: {ratings_dist_chart.total_packs_count}")
    return JsonResponse({
                        'promo_count': ratings_dist_chart.promo_count,
                        'totw_count': ratings_dist_chart.totw_count,
                        'hero_count': ratings_dist_chart.hero_count,
                        'icon_count': ratings_dist_chart.icon_count,
                        'total_packs_count': ratings_dist_chart.total_packs_count[0][0],
                        'labels': [row[0] for row in ratings_dist_chart.ratings_count],
                        'counts': [row[1] for row in ratings_dist_chart.ratings_count]
                        })



def my_packs(request):
    return render(request, 'dashboards/my_packs.html')


def privacy_policy(request):
    return render(request, 'dashboards/privacy_policy.html')


def get_count_of_card_type(raretype):
    """
    This will work out the count of a certain card type. 
    E.g. TOTW - raretype = 3
     
    """
    pass