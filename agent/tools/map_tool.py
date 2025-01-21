from llama_index.core.tools import FunctionTool
from typing import List, Dict, Optional
import json

import nest_asyncio
nest_asyncio.apply()

import requests

from enum import Enum
from typing import List, Dict, Optional, Tuple

class CoordinateType(Enum):
    START = "start"
    MID = "mid"
    DEST = "dest"

class MapTool:
    def __init__(self, user_id: int, websocket_manager=None):
        self.BASE_URL = "http://localhost:80/api/mapbox"

        print('---', user_id, '---')

        self.user_id = user_id

        self.session_token = user_id
        self.websocket_manager = websocket_manager

         # Add coordinate storage
        self.start_coordinate: Optional[Tuple[float, float]] = None
        self.dest_coordinate: Optional[Tuple[float, float]] = None
        self.mid_coordinates: List[Tuple[float, float]] = []

        # Search locations tool
        self.search_locations = FunctionTool.from_defaults(
            fn=self.search_locations_fn,
            description=(
                "Tìm kiếm địa điểm. Tham số:\n"
                "- query (str): Từ khóa tìm kiếm\n"
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
                "- coordinat_type (str): Nhận 1 trong 3 giá trị 'start', 'mid', 'dest'. Muốn set coordinate này đang tìm cho vị trí bắt đầu (start), vị trí kết thúc (dest) hay các vị trí ở giữa (mid)\n"
            )
        )
        
        # Get route tool
        self.get_route = FunctionTool.from_defaults(
            async_fn=self.get_route_fn,
            description=(
                "Lấy chỉ đường giữa các điểm.\n"
            )
        )

    def search_locations_fn(
        self, 
        query: str,
        proximity_longitude: float = None,
        proximity_latitude: float = None
    ) -> Dict:
        """Search for locations using Mapbox API"""
        try:
            url = f"{self.BASE_URL}/suggestions"
            params = {
                "query": query,
                "session_token": self.session_token
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
        coordinate_type: str
    ) -> Dict:
        """Get place details and store coordinates based on type"""
        try:

            url = f"{self.BASE_URL}/retrieve/{mapbox_id}"
            params = {"session_token": self.session_token}
            response = requests.get(url, params=params)

            response.raise_for_status()
            place_data = response.json()
            
            # Extract coordinates
            longitude = float(place_data.get('longitude', 0))
            latitude = float(place_data.get('latitude', 0))
            
            # Store coordinates based on type
            if coordinate_type == CoordinateType.START.value:
                self.start_coordinate = (longitude, latitude)
            elif coordinate_type == CoordinateType.DEST.value:
                self.dest_coordinate = (longitude, latitude)
            elif coordinate_type == CoordinateType.MID.value:
                self.mid_coordinates.append((longitude, latitude))
                
            return place_data
            
        except Exception as e:
            return {"error": str(e)}

    async def get_route_fn(self) -> str:
        """Get route between points and send via WebSocket"""
        if not self.start_coordinate or not self.dest_coordinate:
            raise ValueError("Start and destination coordinates must be set first using get_place_details")

        try:
            url = f"{self.BASE_URL}/route"
            params = {
                "start_longitude": self.start_coordinate[0],
                "start_latitude": self.start_coordinate[1], 
                "dest_longitude": self.dest_coordinate[0],
                "dest_latitude": self.dest_coordinate[1]
            }

            # Add mid points if they exist
            if self.mid_coordinates:
                mid_points = ";".join([f"{lng},{lat}" for lng, lat in self.mid_coordinates])
                params["mid_points"] = mid_points
                
            response = requests.get(url, params=params)
            response.raise_for_status()
            route_data = response.json()

            # Send route data via WebSocket
            if self.websocket_manager:
                await self.websocket_manager.send_personal_message(
                    json.dumps({
                        "event": "route_data", 
                        "data": route_data
                    }),
                    self.user_id
                )
                print("Send data to -", self.user_id)
            else:
                print("No websocket manager")
            
            return "Tôi vừa gửi thông tin về đường đi cho khách hàng"
        except Exception as e:
            return f"Lỗi khi lấy thông tin chỉ đường: {str(e)}"