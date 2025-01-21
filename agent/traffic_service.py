import json
import math
from datetime import datetime

# Load traffic data
with open('traffic_data.json', 'r', encoding='utf-8') as f:
    traffic_data = json.load(f)

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth's radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def check_traffic(current_lat, current_lon):
    # Special coordinate
    if current_lat == 0 and current_lon == 0:
        return 'heavy'
    
    # Tọa độ tâm vòng tròn
    center_lat, center_lon = 10.790167, 106.652426
    # Tọa độ một điểm nằm trên vòng tròn
    circle_point_lat, circle_point_lon = 10.786197, 106.653650
    
    # Tính bán kính vòng tròn (khoảng cách giữa tâm và điểm trên vòng tròn)
    radius = ((circle_point_lat - center_lat) ** 2 + (circle_point_lon - center_lon) ** 2) ** 0.5
    
    # Tính khoảng cách từ điểm hiện tại đến tâm vòng tròn
    distance = ((current_lat - center_lat) ** 2 + (current_lon - center_lon) ** 2) ** 0.5
    
    # Kiểm tra nếu khoảng cách nằm trong vòng tròn
    if distance <= radius:
        return 'heavy'
    


    now = datetime.now()
    current_hour = now.hour

    # Determine current time period
    time_period = None
    if 7 <= current_hour < 9:
        time_period = "7h-9h"
    elif 9 <= current_hour < 11:
        time_period = "9h-11h" 
    elif 11 <= current_hour < 13:
        time_period = "11h-13h"
    elif 13 <= current_hour < 15:
        time_period = "13h-15h"
    elif 15 <= current_hour < 17:
        time_period = "15h-17h"
    elif 17 <= current_hour < 19:
        time_period = "17h-19h"
    elif 19 <= current_hour < 21:
        time_period = "19h-21h"
    else:
        return 'clear'

    congestion_points = traffic_data.get(time_period, [])
    relevant_congestion_points = [
        point for point in congestion_points
        if point['status'].lower() in ['cao', 'rất cao']
    ]

    for point in relevant_congestion_points:
        distance = haversine_distance(
            current_lat, current_lon,
            point['latitude'], point['longitude']
        )
        if distance <= 700:  # Within 700 meters
            return 'heavy'

    return 'clear'