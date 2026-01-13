"""
Geographic data management for EcoTrip Planner

Manages Indian city coordinates, distance calculations, and location services.
"""

from typing import Dict, List, Tuple, Optional
from geopy.distance import geodesic
from .models import GeographicLocation


class GeographicDataManager:
    """Manages geographic data and distance calculations for Indian cities"""
    
    def __init__(self):
        # Major Indian cities with coordinates
        self.indian_cities = {
            'Salem': GeographicLocation('Salem', 'Tamil Nadu', 11.6643, 78.1460, []),
            'Chennai': GeographicLocation('Chennai', 'Tamil Nadu', 13.0827, 80.2707, []),
            'Delhi': GeographicLocation('Delhi', 'Delhi', 28.7041, 77.1025, []),
            'Mumbai': GeographicLocation('Mumbai', 'Maharashtra', 19.0760, 72.8777, []),
            'Bangalore': GeographicLocation('Bangalore', 'Karnataka', 12.9716, 77.5946, []),
            'Kolkata': GeographicLocation('Kolkata', 'West Bengal', 22.5726, 88.3639, []),
            'Hyderabad': GeographicLocation('Hyderabad', 'Telangana', 17.3850, 78.4867, []),
            'Pune': GeographicLocation('Pune', 'Maharashtra', 18.5204, 73.8567, []),
            'Ahmedabad': GeographicLocation('Ahmedabad', 'Gujarat', 23.0225, 72.5714, []),
            'Jaipur': GeographicLocation('Jaipur', 'Rajasthan', 26.9124, 75.7873, []),
            'Kochi': GeographicLocation('Kochi', 'Kerala', 9.9312, 76.2673, []),
            'Goa': GeographicLocation('Goa', 'Goa', 15.2993, 74.1240, []),
            'Agra': GeographicLocation('Agra', 'Uttar Pradesh', 27.1767, 78.0081, []),
            'Varanasi': GeographicLocation('Varanasi', 'Uttar Pradesh', 25.3176, 82.9739, []),
            'Udaipur': GeographicLocation('Udaipur', 'Rajasthan', 24.5854, 73.7125, [])
        }
        
        # Popular route pairs for quick selection
        self.popular_routes = [
            ('Salem', 'Chennai'),
            ('Delhi', 'Mumbai'),
            ('Bangalore', 'Chennai'),
            ('Delhi', 'Goa'),
            ('Mumbai', 'Pune'),
            ('Chennai', 'Kochi'),
            ('Delhi', 'Jaipur'),
            ('Mumbai', 'Goa'),
            ('Bangalore', 'Hyderabad'),
            ('Kolkata', 'Delhi')
        ]
    
    def get_city_coordinates(self, city_name: str) -> Optional[Tuple[float, float]]:
        """Retrieve latitude/longitude for a city"""
        city = self.indian_cities.get(city_name)
        if city:
            return (city.latitude, city.longitude)
        return None
    
    def calculate_geodesic_distance(self, origin: str, destination: str) -> Optional[float]:
        """Calculate accurate distance between two cities in kilometers"""
        origin_coords = self.get_city_coordinates(origin)
        destination_coords = self.get_city_coordinates(destination)
        
        if origin_coords and destination_coords:
            distance = geodesic(origin_coords, destination_coords).kilometers
            return distance
        
        return None
    
    def validate_city_names(self, city_name: str) -> bool:
        """Check if city name exists in the database"""
        return city_name in self.indian_cities
    
    def get_city_suggestions(self, partial_name: str) -> List[str]:
        """Get city name suggestions for partial matches"""
        partial_lower = partial_name.lower()
        suggestions = [
            city for city in self.indian_cities.keys()
            if partial_lower in city.lower()
        ]
        return suggestions[:5]  # Return top 5 matches
    
    def get_popular_routes(self) -> List[Tuple[str, str]]:
        """Get list of popular route pairs"""
        return self.popular_routes
    
    def get_all_cities(self) -> List[str]:
        """Get list of all available cities"""
        return list(self.indian_cities.keys())
    
    def get_city_info(self, city_name: str) -> Optional[GeographicLocation]:
        """Get complete city information"""
        return self.indian_cities.get(city_name)
    
    def calculate_distance(self, origin: str, destination: str) -> float:
        """Calculate distance between two cities in kilometers (alias for calculate_geodesic_distance)"""
        distance = self.calculate_geodesic_distance(origin, destination)
        return distance if distance is not None else 0.0