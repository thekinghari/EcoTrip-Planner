"""
ML-based Route Prediction Model

Predicts route information (distance, duration, alternatives) without requiring
external mapping APIs using geographic data and ML-based estimation.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from .geographic_data import GeographicDataManager
import math


class MLRoutePredictor:
    """Machine learning model for predicting route information"""
    
    def __init__(self):
        """Initialize the route predictor"""
        self.geo_manager = GeographicDataManager()
        
        # Average speeds for different modes in India (km/h)
        self.mode_speeds = {
            'Flight': 500.0,  # Including airport time
            'Train': 60.0,    # Average including stops
            'Car': 50.0,      # Highway + city driving
            'Bus': 45.0       # Including stops
        }
        
        # Buffer times for different modes (hours)
        self.mode_buffers = {
            'Flight': 3.0,    # Airport check-in, security, boarding
            'Train': 1.0,     # Station arrival, boarding
            'Car': 0.5,       # Breaks, fuel stops
            'Bus': 1.0        # Stops, boarding
        }
        
        # Route efficiency factors (how much longer than direct distance)
        self.route_efficiency = {
            'Flight': 1.0,    # Direct routes
            'Train': 1.15,   # Train routes may be longer
            'Car': 1.2,      # Road routes are longer than direct
            'Bus': 1.25      # Bus routes are longest
        }
    
    def predict_distance(self, origin: str, destination: str, 
                        mode: str = 'Car') -> float:
        """
        Predict route distance between two cities
        
        Args:
            origin: Origin city name
            destination: Destination city name
            mode: Transportation mode
        
        Returns:
            Predicted distance in kilometers
        """
        # Get direct geodesic distance
        direct_distance = self.geo_manager.calculate_distance(origin, destination)
        
        if direct_distance <= 0:
            return 0.0
        
        # Apply mode-specific efficiency factor
        efficiency = self.route_efficiency.get(mode, 1.2)
        predicted_distance = direct_distance * efficiency
        
        return round(predicted_distance, 2)
    
    def predict_duration(self, origin: str, destination: str,
                        mode: str = 'Car') -> float:
        """
        Predict travel duration between two cities
        
        Args:
            origin: Origin city name
            destination: Destination city name
            mode: Transportation mode
        
        Returns:
            Predicted duration in hours
        """
        distance = self.predict_distance(origin, destination, mode)
        
        if distance <= 0:
            return 0.0
        
        # Get average speed for mode
        speed = self.mode_speeds.get(mode, 50.0)
        
        # Calculate travel time
        travel_time = distance / speed
        
        # Add buffer time
        buffer = self.mode_buffers.get(mode, 0.5)
        total_time = travel_time + buffer
        
        # Minimum 30 minutes
        return round(max(total_time, 0.5), 2)
    
    def predict_alternative_routes(self, origin: str, destination: str,
                                   modes: Optional[List[str]] = None) -> List[Dict[str, any]]:
        """
        Predict alternative routes for different transportation modes
        
        Args:
            origin: Origin city name
            destination: Destination city name
            modes: List of transportation modes (default: all modes)
        
        Returns:
            List of alternative route predictions
        """
        if modes is None:
            modes = ['Flight', 'Train', 'Car', 'Bus']
        
        alternatives = []
        
        for mode in modes:
            try:
                distance = self.predict_distance(origin, destination, mode)
                duration = self.predict_duration(origin, destination, mode)
                
                if distance > 0:
                    alternative = {
                        'mode': mode,
                        'distance_km': distance,
                        'duration_hours': duration,
                        'origin': origin,
                        'destination': destination,
                        'is_predicted': True,
                        'prediction_method': 'ml_geographic'
                    }
                    alternatives.append(alternative)
            except Exception:
                continue
        
        return alternatives
    
    def predict_route_details(self, origin: str, destination: str,
                             mode: str) -> Dict[str, any]:
        """
        Predict detailed route information
        
        Args:
            origin: Origin city name
            destination: Destination city name
            mode: Transportation mode
        
        Returns:
            Dictionary with route details
        """
        distance = self.predict_distance(origin, destination, mode)
        duration = self.predict_duration(origin, destination, mode)
        
        # Estimate number of stops based on distance and mode
        stops = self._estimate_stops(distance, mode)
        
        return {
            'distance_km': distance,
            'duration_hours': duration,
            'estimated_stops': stops,
            'average_speed_kmh': round(distance / max(duration - self.mode_buffers.get(mode, 0.5), 0.1), 2),
            'route_type': mode,
            'origin': origin,
            'destination': destination,
            'is_predicted': True
        }
    
    def _estimate_stops(self, distance: float, mode: str) -> int:
        """Estimate number of stops based on distance and mode"""
        if mode == 'Flight':
            return 0  # Direct flights
        elif mode == 'Train':
            # Trains stop more frequently
            return max(1, int(distance / 100))
        elif mode == 'Car':
            # Cars may stop for breaks
            return max(0, int(distance / 200))
        elif mode == 'Bus':
            # Buses stop frequently
            return max(1, int(distance / 50))
        else:
            return 0
    
    def compare_routes(self, origin: str, destination: str) -> Dict[str, any]:
        """
        Compare all available routes between two cities
        
        Args:
            origin: Origin city name
            destination: Destination city name
        
        Returns:
            Comparison of all route options
        """
        all_modes = ['Flight', 'Train', 'Car', 'Bus']
        routes = []
        
        for mode in all_modes:
            details = self.predict_route_details(origin, destination, mode)
            routes.append(details)
        
        # Sort by duration
        routes.sort(key=lambda x: x['duration_hours'])
        
        return {
            'origin': origin,
            'destination': destination,
            'routes': routes,
            'fastest_mode': routes[0]['route_type'] if routes else None,
            'shortest_distance': min(r['distance_km'] for r in routes) if routes else 0.0
        }
    
    def get_route_recommendations(self, origin: str, destination: str,
                                  preferences: Optional[Dict[str, any]] = None) -> List[Dict[str, any]]:
        """
        Get route recommendations based on preferences
        
        Args:
            origin: Origin city name
            destination: Destination city name
            preferences: User preferences (e.g., {'priority': 'speed', 'max_duration': 10})
        
        Returns:
            List of recommended routes
        """
        if preferences is None:
            preferences = {'priority': 'speed'}
        
        all_routes = self.compare_routes(origin, destination)
        
        routes = all_routes['routes']
        
        # Filter by preferences
        if 'max_duration' in preferences:
            routes = [r for r in routes if r['duration_hours'] <= preferences['max_duration']]
        
        if 'max_distance' in preferences:
            routes = [r for r in routes if r['distance_km'] <= preferences['max_distance']]
        
        # Sort by priority
        priority = preferences.get('priority', 'speed')
        if priority == 'speed':
            routes.sort(key=lambda x: x['duration_hours'])
        elif priority == 'distance':
            routes.sort(key=lambda x: x['distance_km'])
        elif priority == 'comfort':
            # Assume Flight > Train > Car > Bus for comfort
            comfort_order = {'Flight': 4, 'Train': 3, 'Car': 2, 'Bus': 1}
            routes.sort(key=lambda x: comfort_order.get(x['route_type'], 0), reverse=True)
        
        return routes

