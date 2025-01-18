from llama_index.core.tools import FunctionTool
from typing import List, Dict, Optional
import requests

class MapTool:
    def __init__(self):
        self.BASE_URL = "http://localhost:80/api/mapbox"
        
        # Search locations tool
        self.search_locations = FunctionTool.from_defaults(
            fn=self.search_locations_fn,
            description=(
                "Tìm kiếm địa điểm. Tham số:\n"
                "- query (str): Từ khóa tìm kiếm\n"
                "- session_token (str): Token phiên làm việc\n"
                "- proximity_longitude (float, optional): Kinh độ vị trí gần đó\n"
                "- proximity_latitude (float, optional): Vĩ độ vị trí gần đó"
            )
        )
        
        # Get place details tool  
        self.get_place_details = FunctionTool.from_defaults(
            fn=self.get_place_details_fn,
            description=(
                "Lấy chi tiết của một địa điểm. Tham số:\n"
                "- mapbox_id (str): ID của địa điểm từ Mapbox\n"
                "- session_token (str): Token phiên làm việc"
            )
        )
        
        # Get route tool
        self.get_route = FunctionTool.from_defaults(
            fn=self.get_route_fn,
            description=(
                "Lấy chỉ đường giữa các điểm. Tham số:\n"
                "- start_longitude (float): Kinh độ điểm bắt đầu\n" 
                "- start_latitude (float): Vĩ độ điểm bắt đầu\n"
                "- dest_longitude (float): Kinh độ điểm đích\n"
                "- dest_latitude (float): Vĩ độ điểm đích\n"
                "- mid_points (str, optional): Các điểm dừng giữa đường, định dạng: 'lng1,lat1;lng2,lat2'"
            )
        )

    def search_locations_fn(
        self, 
        query: str,
        session_token: str,
        proximity_longitude: float = None,
        proximity_latitude: float = None
    ) -> Dict:
        """Search for locations using Mapbox API"""
        try:
            url = f"{self.BASE_URL}/suggestions"
            params = {
                "query": query,
                "session_token": session_token
            }
            if proximity_longitude and proximity_latitude:
                params.update({
                    "proximity_longitude": proximity_longitude,
                    "proximity_latitude": proximity_latitude
                })
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"Lỗi khi tìm kiếm địa điểm: {str(e)}"}

    def get_place_details_fn(
        self,
        mapbox_id: str,
        session_token: str
    ) -> Dict:
        """Get details for a specific place"""
        try:
            url = f"{self.BASE_URL}/retrieve/{mapbox_id}"
            params = {"session_token": session_token}
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"Lỗi khi lấy thông tin địa điểm: {str(e)}"}

    def get_route_fn(
        self,
        start_longitude: float,
        start_latitude: float,
        dest_longitude: float,
        dest_latitude: float,
        mid_points: str = None
    ) -> Dict:
        """Get route between points"""
        try:
            url = f"{self.BASE_URL}/route"
            params = {
                "start_longitude": start_longitude,
                "start_latitude": start_latitude,
                "dest_longitude": dest_longitude,
                "dest_latitude": dest_latitude
            }
            if mid_points:
                params["mid_points"] = mid_points
                
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"Lỗi khi lấy thông tin chỉ đường: {str(e)}"}