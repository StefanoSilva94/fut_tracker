from django.shortcuts import render
from django.db import connection
from .charts.chart_utils import create_time_query_filter
from django.http import JsonResponse
import json



def home(request):
    with connection.cursor() as cursor:
        
        
        cursor.execute("SELECT COUNT(DISTINCT(pack_id)) FROM packed_items")
        total_packs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT(pack_id)) FROM player_picks")
        total_picks = cursor.fetchone()[0]
        
        cursor.execute("SELECT DISTINCT(pack_name) FROM packed_items")
        pack_names = cursor.fetchall()
        
        # Flatten the list of tuples
        pack_names = [name[0] for name in pack_names] 
  
    return render(request, 'dashboards/home.html', 
                  {'total_packs': total_packs,
                   'total_picks': total_picks,
                   'pack_names': pack_names,
                   })


def get_pack_data(request):
    """
    This will filter by a pack name and get the count of each rating for that pack.
    """
    data = json.loads(request.body)
    print(data)
    pack = data.get('pack', 'all')  # Get pack selection
    time_filter = data.get('time', 'all')  # Get time filter selection
    time_filter_query = create_time_query_filter(time_filter)

    # Base query
    query = """SELECT rating, COUNT(*) AS rating_count 
               FROM packed_items 
               WHERE pack_name = %s"""
    
    params = [pack]

    if time_filter_query:
        query += " AND " + time_filter_query

    query += " GROUP BY rating ORDER BY rating"

    # Debugging: Print the query before execution
    print("Executing query:", query)
    print(f"Parameters: {params}")

    # Execute the query
    with connection.cursor() as cursor:
        cursor.execute(query, params)  # Use parameterized query
        ratings_count = cursor.fetchall()

    # Prepare the response
    labels = [row[0] for row in ratings_count]  # Extract ratings
    counts = [row[1] for row in ratings_count]  # Extract counts
    
    # Debugging: Print the results
    print("Ratings Count:", ratings_count)
    print(f"pack = {pack}")
    print(f"time = {time_filter}")

    return JsonResponse({
        'labels': labels,
        'counts': counts
    })


def my_packs(request):
    return render(request, 'dashboards/my_packs.html')

    
def chart_view(request):
    # Example data to pass to the chart
    chart_data = {
        'labels': ['January', 'February', 'March', 'April', 'May'],
        'data': [10, 20, 30, 40, 50]
    }
    return render(request, 'dashboards/chart.html', {'chart_data': chart_data})