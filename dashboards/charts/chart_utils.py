from datetime import datetime, timedelta

def create_time_query_filter(timestamp_filter):
    """
    This will create a string to filter a query by a timestamp column in the range of timestamp_filter to current date
    """
    time_filter_query = ""
    current_date = datetime.now()
    
    if timestamp_filter == 'all_time':
        pass
    elif timestamp_filter == '1_week':
        one_week_ago = current_date - timedelta(days=7)
        time_filter_query = f"created_at > '{one_week_ago.strftime('%Y-%m-%d')}'"
    elif timestamp_filter == 'since_friday':
        # get data since last friday 6pm
        days_since_friday = (current_date.weekday() - 4) % 7
        last_friday = current_date - timedelta(days=days_since_friday)
        
        # Set last Friday's time to 6 PM (18:00:00)
        last_friday_6pm = last_friday.replace(hour=18, minute=0, second=0, microsecond=0)
        
        time_filter_query = f"created_at > '{last_friday_6pm.strftime('%Y-%m-%d %H:%M:%S')}'"
        
    return time_filter_query
        
        