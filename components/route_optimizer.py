"""
Route optimizer for EcoTrip Planner

Generates multiple alternate routes with intermediate waypoints and cities
to optimize for distance, time, and carbon emissions.
"""

from typing import Dict, List, Tuple, Optional, Any
from geopy.distance import geodesic
from .geographic_data import GeographicDataManager
import logging


class RouteOptimizer:
    """Optimizes routes by finding intermediate cities and generating alternate paths"""
    
    def __init__(self):
        self.geo_manager = GeographicDataManager()
        
        # Predefined intermediate cities for popular routes (can be extended)
        # Format: (origin, destination): [list of intermediate cities]
        # Includes shortcuts and efficient paths
        self.route_waypoints = {
            ('Chennai', 'Coimbatore'): ['Vellore', 'Salem', 'Erode', 'Tiruppur'],
            ('Coimbatore', 'Chennai'): ['Tiruppur', 'Erode', 'Salem', 'Vellore'],
            ('Bangalore', 'Chennai'): ['Vellore', 'Kanchipuram', 'Tiruvallur'],
            ('Chennai', 'Bangalore'): ['Tiruvallur', 'Kanchipuram', 'Vellore'],
            ('Delhi', 'Mumbai'): ['Jaipur', 'Ajmer', 'Ahmedabad', 'Vadodara'],
            ('Mumbai', 'Delhi'): ['Vadodara', 'Ahmedabad', 'Ajmer', 'Jaipur'],
            ('Chennai', 'Madurai'): ['Vellore', 'Salem', 'Tiruchirappalli'],
            ('Madurai', 'Chennai'): ['Tiruchirappalli', 'Salem', 'Vellore'],
            ('Salem', 'Coimbatore'): ['Erode', 'Tiruppur'],
            ('Coimbatore', 'Salem'): ['Tiruppur', 'Erode'],
        }
        
        # Shortcut routes - routes that are shorter or more efficient
        # Format: (origin, destination): [list of intermediate cities for shortcut]
        self.shortcut_routes = {
            ('Chennai', 'Coimbatore'): {
                'shortcut_via_salem': ['Salem'],  # Shorter via Salem
                'direct': [],  # Direct route
                'scenic_via_vellore': ['Vellore', 'Salem']  # Alternative via Vellore
            },
            ('Coimbatore', 'Chennai'): {
                'shortcut_via_salem': ['Salem'],
                'direct': [],
                'scenic_via_vellore': ['Salem', 'Vellore']
            }
        }
    
    def find_intermediate_cities(self, origin: str, destination: str, max_waypoints: int = 3) -> List[str]:
        """Find intermediate cities along the route between origin and destination"""
        
        # Check if we have predefined waypoints for this route
        route_key = (origin, destination)
        if route_key in self.route_waypoints:
            return self.route_waypoints[route_key][:max_waypoints]
        
        # Reverse route check
        reverse_key = (destination, origin)
        if reverse_key in self.route_waypoints:
            # Return reverse of waypoints
            waypoints = self.route_waypoints[reverse_key][:max_waypoints]
            return list(reversed(waypoints))
        
        # Calculate intermediate cities dynamically
        return self._calculate_intermediate_cities(origin, destination, max_waypoints)
    
    def _calculate_intermediate_cities(self, origin: str, destination: str, max_waypoints: int) -> List[str]:
        """Dynamically calculate intermediate cities based on geographic proximity"""
        origin_coords = self.geo_manager.get_city_coordinates(origin)
        dest_coords = self.geo_manager.get_city_coordinates(destination)
        
        if not origin_coords or not dest_coords:
            return []
        
        origin_lat, origin_lon = origin_coords
        dest_lat, dest_lon = dest_coords
        
        # Get all cities
        all_cities = self.geo_manager.get_all_cities()
        intermediate_candidates = []
        
        # Calculate perpendicular distance from each city to the route line
        for city_name in all_cities:
            if city_name in [origin, destination]:
                continue
            
            city_coords = self.geo_manager.get_city_coordinates(city_name)
            if not city_coords:
                continue
            
            city_lat, city_lon = city_coords
            
            # Calculate if city is roughly between origin and destination
            # Check if city is within the bounding box of origin-destination
            min_lat, max_lat = min(origin_lat, dest_lat), max(origin_lat, dest_lat)
            min_lon, max_lon = min(origin_lon, dest_lon), max(origin_lon, dest_lon)
            
            # Expand bounding box slightly (10% buffer)
            lat_range = max_lat - min_lat
            lon_range = max_lon - min_lon
            buffer_lat = lat_range * 0.1
            buffer_lon = lon_range * 0.1
            
            if not (min_lat - buffer_lat <= city_lat <= max_lat + buffer_lat and
                    min_lon - buffer_lon <= city_lon <= max_lon + buffer_lon):
                continue
            
            # Calculate perpendicular distance from city to route line
            # Using point-to-line distance formula
            dist_to_origin = geodesic(origin_coords, city_coords).kilometers
            dist_to_dest = geodesic(city_coords, dest_coords).kilometers
            total_dist = geodesic(origin_coords, dest_coords).kilometers
            
            # City should not be too far from the route
            # Accept cities within 50km perpendicular distance
            if dist_to_origin + dist_to_dest <= total_dist * 1.5:  # Within reasonable deviation
                # Calculate progress along route (0 to 1)
                progress = dist_to_origin / (dist_to_origin + dist_to_dest) if (dist_to_origin + dist_to_dest) > 0 else 0
                
                intermediate_candidates.append({
                    'city': city_name,
                    'progress': progress,
                    'distance': dist_to_origin + dist_to_dest
                })
        
        # Sort by progress along route and select evenly spaced waypoints
        intermediate_candidates.sort(key=lambda x: x['progress'])
        
        if len(intermediate_candidates) == 0:
            return []
        
        # Select up to max_waypoints cities, evenly distributed
        selected_cities = []
        if max_waypoints == 1:
            # Take middle city
            selected_cities.append(intermediate_candidates[len(intermediate_candidates) // 2]['city'])
        else:
            # Distribute waypoints evenly
            step = len(intermediate_candidates) / (max_waypoints + 1)
            for i in range(1, max_waypoints + 1):
                idx = int(i * step)
                if idx < len(intermediate_candidates):
                    selected_cities.append(intermediate_candidates[idx]['city'])
        
        return selected_cities[:max_waypoints]
    
    def generate_alternate_routes(self, origin: str, destination: str, 
                                 num_routes: int = 3) -> List[Dict[str, Any]]:
        """Generate multiple alternate routes with different waypoints including shortcuts"""
        alternate_routes = []
        
        # Check if we have predefined shortcut routes
        route_key = (origin, destination)
        has_shortcuts = route_key in self.shortcut_routes
        
        # Route 1: Direct route (no waypoints)
        direct_route = {
            'route_id': 'direct',
            'name': 'Direct Route',
            'waypoints': [],
            'description': 'Shortest direct path between origin and destination',
            'is_direct': True,
            'is_shortcut': False
        }
        alternate_routes.append(direct_route)
        
        # If we have shortcut routes, add them first
        if has_shortcuts:
            shortcuts = self.shortcut_routes[route_key]
            for shortcut_id, waypoints in shortcuts.items():
                if waypoints != []:  # Skip direct route as it's already added
                    shortcut_name = 'Shortcut via ' + ', '.join(waypoints) if waypoints else 'Shortcut Route'
                    shortcut_route = {
                        'route_id': shortcut_id,
                        'name': shortcut_name,
                        'waypoints': waypoints,
                        'description': f'Efficient shortcut route via {", ".join(waypoints)} - reduces distance and carbon footprint',
                        'is_direct': False,
                        'is_shortcut': True
                    }
                    alternate_routes.append(shortcut_route)
        
        # Route 2-N: Routes with intermediate waypoints
        intermediate_cities = self.find_intermediate_cities(origin, destination, max_waypoints=3)
        
        if intermediate_cities:
            # Create routes with different combinations of waypoints
            
            # Route with middle waypoint only (often most efficient)
            if len(intermediate_cities) >= 1:
                middle_idx = len(intermediate_cities) // 2
                middle_city = intermediate_cities[middle_idx]
                # Check if this route is not already added as a shortcut
                if not any(r['waypoints'] == [middle_city] for r in alternate_routes):
                    middle_route = {
                        'route_id': 'via_middle',
                        'name': f'Via {middle_city}',
                        'waypoints': [middle_city],
                        'description': f'Balanced route via {middle_city} - good distance and road conditions',
                        'is_direct': False,
                        'is_shortcut': False
                    }
                    alternate_routes.append(middle_route)
            
            # Route with first waypoint (closer to origin)
            if len(intermediate_cities) >= 1:
                first_city = intermediate_cities[0]
                if not any(r['waypoints'] == [first_city] for r in alternate_routes):
                    first_route = {
                        'route_id': 'via_first',
                        'name': f'Via {first_city}',
                        'waypoints': [first_city],
                        'description': f'Route via {first_city} - passes through northern/middle section',
                        'is_direct': False,
                        'is_shortcut': False
                    }
                    alternate_routes.append(first_route)
            
            # Route with last waypoint (closer to destination)
            if len(intermediate_cities) >= 2:
                last_city = intermediate_cities[-1]
                if not any(r['waypoints'] == [last_city] for r in alternate_routes):
                    last_route = {
                        'route_id': 'via_last',
                        'name': f'Via {last_city}',
                        'waypoints': [last_city],
                        'description': f'Route via {last_city} - passes through southern/middle section',
                        'is_direct': False,
                        'is_shortcut': False
                    }
                    alternate_routes.append(last_route)
            
            # Route with all waypoints (scenic route)
            if len(intermediate_cities) >= 2:
                if not any(r['waypoints'] == intermediate_cities for r in alternate_routes):
                    full_route = {
                        'route_id': 'via_all',
                        'name': f'Scenic Route via {", ".join(intermediate_cities)}',
                        'waypoints': intermediate_cities,
                        'description': f'Scenic route passing through {len(intermediate_cities)} cities - longer but covers more places',
                        'is_direct': False,
                        'is_shortcut': False
                    }
                    alternate_routes.append(full_route)
        
        # Limit to requested number of routes, but prioritize shortcuts and efficient routes
        # Sort routes: shortcuts first, then direct, then others
        route_priority = {
            'shortcut': 1,
            'direct': 2,
            'via_middle': 3,
            'via_first': 4,
            'via_last': 5,
            'via_all': 6
        }
        
        # Sort routes by priority
        alternate_routes.sort(key=lambda x: route_priority.get(x['route_id'], 10))
        
        return alternate_routes[:num_routes]
    
    def calculate_route_distance(self, origin: str, destination: str, 
                                waypoints: List[str]) -> float:
        """Calculate total distance for a route with waypoints"""
        total_distance = 0.0
        route_path = [origin] + waypoints + [destination]
        
        for i in range(len(route_path) - 1):
            segment_distance = self.geo_manager.calculate_geodesic_distance(
                route_path[i], route_path[i + 1]
            )
            if segment_distance:
                total_distance += segment_distance
            else:
                # Fallback: use straight-line distance
                coords1 = self.geo_manager.get_city_coordinates(route_path[i])
                coords2 = self.geo_manager.get_city_coordinates(route_path[i + 1])
                if coords1 and coords2:
                    total_distance += geodesic(coords1, coords2).kilometers
        
        return total_distance
    
    def get_route_coordinates(self, origin: str, destination: str, 
                             waypoints: List[str]) -> List[Tuple[float, float]]:
        """Get list of coordinates for a route with waypoints"""
        coordinates = []
        route_path = [origin] + waypoints + [destination]
        
        for city in route_path:
            coords = self.geo_manager.get_city_coordinates(city)
            if coords:
                coordinates.append(coords)
        
        return coordinates
    
    def optimize_for_distance(self, origin: str, destination: str) -> Dict[str, Any]:
        """Find the route with minimum distance"""
        alternate_routes = self.generate_alternate_routes(origin, destination, num_routes=5)
        
        best_route = None
        min_distance = float('inf')
        
        for route in alternate_routes:
            distance = self.calculate_route_distance(
                origin, destination, route['waypoints']
            )
            route['distance_km'] = distance
            
            if distance < min_distance:
                min_distance = distance
                best_route = route
        
        return best_route or alternate_routes[0] if alternate_routes else None
    
    def optimize_for_emissions(self, origin: str, destination: str, 
                              mode: str = 'Car') -> Dict[str, Any]:
        """Find the route with minimum emissions (shorter distance typically means less emissions)"""
        # For most modes, shorter distance = less emissions
        return self.optimize_for_distance(origin, destination)
