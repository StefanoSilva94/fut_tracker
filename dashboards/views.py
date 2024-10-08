from django.shortcuts import render
from django.db import connection
from .charts.chart_utils import create_time_query_filter
from django.http import JsonResponse
from .charts import charts
import json
from django.contrib.auth.decorators import login_required
from .models import Player
from django.core.paginator import Paginator
import csv
from django.http import StreamingHttpResponse, HttpResponseForbidden
from io import StringIO



def home(request):
    with connection.cursor() as cursor:
        
        cursor.execute("SELECT COUNT(DISTINCT(pack_id)) FROM packed_items")
        total_packs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT(pack_id)) FROM player_picks")
        total_picks = cursor.fetchone()[0]
        
        cursor.execute("SELECT DISTINCT(pack_name) FROM packed_items ORDER BY pack_name")
        pack_names = cursor.fetchall()
        
        cursor.execute("SELECT DISTINCT(pack_name) FROM player_picks ORDER BY pack_name")
        pick_names = cursor.fetchall()
        
        # Flatten the list of tuples
        pack_names = [name[0] for name in pack_names] 
        pick_names = [name[0] for name in pick_names] 
        
        pack_counts = get_counts_of_card_types('packed_items')
        pick_counts = get_counts_of_card_types('player_picks')
        
        totw_count = pack_counts.get('totw_count', 0) + pick_counts.get('totw_count', 0)
        promo_count = pack_counts.get('promo_count', 0) + pick_counts.get('promo_count', 0)
    return render(request, 'dashboards/home.html', 
                  {'total_packs': total_packs,
                   'total_picks': total_picks,
                   'pack_names': pack_names,
                   'pick_names': pick_names,
                   'total_totws': totw_count,
                   'total_promos': promo_count
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
                        'average_pack_value': ratings_dist_chart.average_pack_value[0],
                        'labels': [row[0] for row in ratings_dist_chart.ratings_count],
                        'counts': [row[1] for row in ratings_dist_chart.ratings_count]
                        })



def my_packs(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        
        pack_counts = get_counts_of_card_types('packed_items', user_id=user_id)
        pick_counts = get_counts_of_card_types('player_picks', user_id=user_id)
        
        totw_count = pack_counts.get('totw_count', 0) + pick_counts.get('totw_count', 0)
        promo_count = pack_counts.get('promo_count', 0) + pick_counts.get('promo_count', 0)
        
        packed_items = []
        
        with connection.cursor() as cursor:
        
            cursor.execute("SELECT COUNT(DISTINCT(pack_id)) FROM packed_items WHERE user_id = %s", [user_id])
            my_packs = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT(pack_id)) FROM player_picks WHERE user_id = %s", [user_id])
            my_picks = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT name AS player, pack_name, rating, position, price, DATE(created_at) AS date
                FROM packed_items
                WHERE user_id = %s
                ORDER BY created_at DESC
            """, [user_id])
            packed_items = cursor.fetchall()
            
        # Pagination setup (using list of tuples returned by fetchall)
        paginator = Paginator(packed_items, 10)  # Show 10 items per page
        page_number = request.GET.get('page')
        paginated_items = paginator.get_page(page_number)        
        
        return render(request, 'dashboards/my_packs.html', 
                      {
                        "title": "My Packs",
                        "my_packs": my_packs,
                        "my_picks": my_picks,
                        "my_totws": totw_count,
                        'my_promos': promo_count,
                        'packed_items': paginated_items
                          })
    else:
        return render(request, 'dashboards/please_log_in.html', {"title": "Log In Needed"})


def privacy_policy(request):
    return render(request, 'dashboards/privacy_policy.html')

    
def about_view(request):
    return render(request, "dashboards/about.html")


def get_counts_of_card_types(table_name, pack_name=None, user_id=None):
    """
    This will work out the count of a certain card type. 
    E.g. TOTW - raretype = 3
    """
    
    # Validate that the table name is safe (optional step)
    allowed_tables = ['packed_items', 'player_picks']  # List of allowed table names
    if table_name not in allowed_tables:
        raise ValueError("Invalid table name")
    
    count_query = f"""
        SELECT
            COUNT(CASE WHEN CAST(raretype AS int) NOT IN (0, 1, 3, 50, 51, 52, 1004) THEN 1 END) AS promo_count,
            COUNT(CASE WHEN CAST(raretype AS int) = 3 THEN 1 END) AS totw_count,
            COUNT(CASE WHEN CAST(raretype AS int) IN (72, 161) THEN 1 END) AS hero_count,
            COUNT(CASE WHEN CAST(raretype AS int) = 12 THEN 1 END) AS icon_count,
            COUNT(CASE WHEN CAST(raretype AS int) = 1 THEN 1 END) AS normal_count
        FROM 
            {table_name}
    """
    
    filters = []
    params = []
    
    if pack_name:
        filters.append("pack_name = %s")
        params.append(pack_name)
    
    if user_id:
        filters.append("user_id = %s")
        params.append(user_id)
    
    if filters:
        count_query += " WHERE " + " AND ".join(filters)
    
    # Execute the query
    with connection.cursor() as cursor:
        cursor.execute(count_query, params)
        counts = cursor.fetchone()

    return { 
            'promo_count': counts[0],
            'totw_count': counts[1],
            'hero_count': counts[2],
            'icon_count': counts[3]
            }
    
def generate_csv(user_id):
    # Use a cursor to execute the raw SQL query
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name AS player, rating, position, price, pack_name, DATE(created_at) AS date
            FROM packed_items
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, [user_id])
        
        # Write the header row
        yield ','.join(['Player', 'Rating', 'Position', 'Price', 'Pack', 'Date']) + '\n'
        
        # Fetch and yield each row
        for item in cursor.fetchall():
            yield ','.join(map(str, item)) + '\n'

def export_packed_items(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        
        # Prepare the CSV response
        response = StreamingHttpResponse(generate_csv(user_id), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="packed_items.csv"'
        
        return response
    else:
        # Return a forbidden response or redirect to login
        return HttpResponseForbidden("You are not authorized to access this resource.")
    
