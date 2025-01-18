from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import httpx
from typing import Dict, Any

router = APIRouter()

MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoibWluaGhpZXUxMSIsImEiOiJjbTU4OWdkaXA0MXg3Mmtwa2ZnMXBnbGpvIn0.VcU6Q0FhEgmHMIjSHhu2gA"

class Coordinate(BaseModel):
    latitude: float
    longitude: float

class SearchRequest(BaseModel):
    query: str
    session_token: str
    proximity: Optional[Coordinate] = None

class RouteRequest(BaseModel):
    start_location: Coordinate
    destination: Coordinate
    mid_points: Optional[List[Coordinate]] = []

@router.get("/suggestions")
async def get_suggestions(
    query: str,
    session_token: str,
    proximity_longitude: Optional[float] = None,
    proximity_latitude: Optional[float] = None
):
    """Get location suggestions from Mapbox Search API"""
    try:
        url = f"https://api.mapbox.com/search/searchbox/v1/suggest"
        params = {
            "q": query,
            "access_token": MAPBOX_ACCESS_TOKEN,
            "session_token": session_token,
            "language": "en",
            "country": "vn"
        }

        if proximity_longitude is not None and proximity_latitude is not None:
            params["proximity"] = f"{proximity_longitude},{proximity_latitude}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            suggestions = {
                "suggestions": [
                    {
                        "name": suggestion.get("name", ""),
                        "mapbox_id": suggestion.get("mapbox_id", ""),
                        "full_address": suggestion.get("full_address", "")
                    }
                    for suggestion in data.get("suggestions", [])
                ]
            }
            
            return suggestions

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/retrieve/{mapbox_id}")
async def retrieve_place(mapbox_id: str, session_token: str):
    """Retrieve place details from Mapbox"""
    try:
        url = f"https://api.mapbox.com/search/searchbox/v1/retrieve/{mapbox_id}"
        params = {
            "access_token": MAPBOX_ACCESS_TOKEN,
            "session_token": session_token
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data["features"] and len(data["features"]) > 0:
                feature = data["features"][0]
                return {
                    "name": feature["properties"]["name"],
                    "full_address": feature["properties"]["full_address"],
                    "coordinates": {
                        "latitude": feature["properties"]["coordinates"]["latitude"],
                        "longitude": feature["properties"]["coordinates"]["longitude"]
                    }
                }
            return {"error": "No location found"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving place details: {str(e)}")

@router.get("/route")
async def get_route(
    start_longitude: float,
    start_latitude: float,
    dest_longitude: float,
    dest_latitude: float,
    mid_points: Optional[str] = None  # Format: "lng1,lat1;lng2,lat2;..."
):
    """Get route from Mapbox Directions API"""
    try:
        # Start with start location coordinates
        coordinates = [f"{start_longitude},{start_latitude}"]
        
        # Add mid points if they exist
        if mid_points:
            mid_point_list = mid_points.split(";")
            coordinates.extend(mid_point_list)
        
        # Add destination coordinates
        coordinates.append(f"{dest_longitude},{dest_latitude}")
        
        # Join all coordinates with semicolon
        coordinates_str = ";".join(coordinates)
        
        url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{coordinates_str}"
        params = {
            "geometries": "geojson",
            "steps": "true",
            "overview": "full",
            "access_token": MAPBOX_ACCESS_TOKEN
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching route: {str(e)}")