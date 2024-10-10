from datetime import datetime, timedelta
from django.db import connection


class baseChart():
    def __init__(self, pack_or_pick, pack_name, time_filter='all_time'):
        self.pack_or_pick = pack_or_pick
        self.time_filter = time_filter
        self.pack_name = pack_name
        self.table_name = 'packed_items' if self.pack_or_pick == 'pack' else 'player_picks'
        
        
    def create_time_query_filter(self):
        """
        This will create a string to filter a query by a timestamp column in the range of timestamp_filter to current date
        It will be appened onto a query to filter by the desired time stamp
        """
        time_filter_query = ""
        current_date = datetime.now()
        
        if self.time_filter == 'all_time':
            time_filter_query = f"created_at <= '{current_date}'"
        elif self.time_filter == '1_week':
            one_week_ago = current_date - timedelta(days=7)
            time_filter_query = f"created_at > '{one_week_ago.strftime('%Y-%m-%d')}'"
        elif self.time_filter == 'since_friday':
            # get data since last friday 6pm
            days_since_friday = (current_date.weekday() - 4) % 7
            last_friday = current_date - timedelta(days=days_since_friday)
            
            # Set last Friday's time to 6 PM (18:00:00)
            last_friday_6pm = last_friday.replace(hour=18, minute=0, second=0, microsecond=0)
            
            time_filter_query = f"created_at > '{last_friday_6pm.strftime('%Y-%m-%d %H:%M:%S')}'"
            
        return time_filter_query
    
        
class ratingsDistributionsChart(baseChart):
    """
    Class to create an object to populate a ratings distribution
    """
        
    def get_data(self):
        time_filter_query = self.create_time_query_filter()
        
        ratings_count_query = f"""
            SELECT rating, COUNT(*) AS rating_count 
            FROM {self.table_name}
            WHERE pack_name = '{self.pack_name}' AND {time_filter_query}
            GROUP BY rating 
            ORDER BY rating
        """
        card_type_query = f"""
            SELECT
                COUNT(CASE WHEN CAST(raretype AS int) NOT IN (0,1, 3, 50, 51, 52, 1004) THEN 1 END) AS promo_count,
                COUNT(CASE WHEN CAST(raretype AS int) = 3 THEN 1 END) AS totw_count,
                COUNT(CASE WHEN CAST(raretype AS int) IN (72, 161) THEN 1 END) AS hero_count,
                COUNT(CASE WHEN CAST(raretype AS int) = 12 THEN 1 END) AS icon_count,
                COUNT(CASE WHEN CAST(raretype AS int) = 1 THEN 1 END) AS normal_count
            FROM 
                {self.table_name}
            WHERE
                pack_name = '{self.pack_name}' AND {time_filter_query}
        """
        total_packs_query = f"""
            SELECT COUNT(*) AS pack_count 
            FROM packs
            WHERE pack_name = '{self.pack_name}' AND {time_filter_query}
        """ 
        
        
        average_pack_value_query = f"""
                                SELECT CAST(AVG(pack_value) AS INT) AS avg_pack_value FROM packs
                                WHERE pack_name = '{self.pack_name}'
        
                               """
        print(total_packs_query)
                                
        with connection.cursor() as cursor:
            try:
                cursor.execute(ratings_count_query, [self.pack_name])
                self.ratings_count = cursor.fetchall()
                
                cursor.execute(total_packs_query)
                self.total_packs_count = cursor.fetchall()
                
                cursor.execute(average_pack_value_query)
                self.average_pack_value = cursor.fetchone()
                
                cursor.execute(card_type_query, [self.pack_name])
                card_type_count = cursor.fetchall()
                self.promo_count = card_type_count[0][0]
                self.totw_count = card_type_count[0][1]
                self.hero_count = card_type_count[0][2]
                self.icon_count = card_type_count[0][3]
                
            except Exception as e:
                print(f"An error occurred: {e}")

                    
        