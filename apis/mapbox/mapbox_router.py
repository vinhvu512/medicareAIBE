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
async def get_suggestions(request: SearchRequest):
    """Get location suggestions from Mapbox Search API"""
    try:
        url = f"https://api.mapbox.com/search/searchbox/v1/suggest"
        params = {
            "q": request.query,
            "access_token": MAPBOX_ACCESS_TOKEN,
            "session_token": request.session_token,
            "language": "en"
        }

        # Add proximity parameter if provided
        if request.proximity:
            params["proximity"] = f"{request.proximity.longitude},{request.proximity.latitude}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Filter and transform suggestions
            simplified_suggestions = [
                {
                    "name": suggestion["name"],
                    "mapbox_id": suggestion["mapbox_id"],
                    "full_address": suggestion["full_address"]
                }
                for suggestion in data["suggestions"]
            ]
            return simplified_suggestions
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
async def get_route(request: RouteRequest):
    """Get route from Mapbox Directions API"""
    try:
        # Start with start location coordinates
        coordinates = [f"{request.start_location.longitude},{request.start_location.latitude}"]
        
        # Add mid points if they exist
        if request.mid_points:
            coordinates.extend([
                f"{point.longitude},{point.latitude}" 
                for point in request.mid_points
            ])
        
        # Add destination coordinates
        coordinates.append(f"{request.destination.longitude},{request.destination.latitude}")
        
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