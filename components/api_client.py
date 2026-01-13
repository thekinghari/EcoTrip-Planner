"""
API client components for EcoTrip Planner

Handles external API integrations with Climatiq and Google Maps APIs,
including error handling, retry logic, rate limiting, and fallback mechanisms.
"""

import os
import requests
from typing import Dict, Any, Optional, List
import time
import logging
from datetime import datetime, timedelta


class APIClientManager:
    """Manages external API communications with error handling and retry logic"""
    
    def __init__(self):
        self.climatiq_api_key = os.getenv('CLIMATIQ_API_KEY')
        self.google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        self.climatiq_base_url = "https://beta3.api.climatiq.io"
        self.google_maps_base_url = "https://maps.googleapis.com/maps/api"
        
        # Rate limiting tracking
        self._last_climatiq_request = None
        self._last_google_maps_request = None
        self._climatiq_request_count = 0
        self._google_maps_request_count = 0
        self._rate_limit_window_start = datetime.now()
        
        # Rate limits (requests per minute)
        self.climatiq_rate_limit = 60
        self.google_maps_rate_limit = 100
        
        # Static emission factors as fallback
        self.static_emission_factors = {
            'Flight': 0.255,  # kg CO2e per km per person
            'Train': 0.041,   # kg CO2e per km per person
            'Car': 0.171,     # kg CO2e per km per person
            'Bus': 0.089,     # kg CO2e per km per person
            'Hotel': 30.0     # kg CO2e per night per person
        }
    
    def query_climatiq_api(self, endpoint: str, data: Dict[str, Any], max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Query Climatiq API with authentication, retry logic, and comprehensive error handling"""
        if not self.climatiq_api_key:
            return None
        
        # Check rate limits before making request
        if not self._check_rate_limit('climatiq'):
            return None
        
        headers = {
            'Authorization': f'Bearer {self.climatiq_api_key}',
            'Content-Type': 'application/json'
        }
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Apply rate limiting delay
                self._apply_rate_limit_delay('climatiq')
                
                response = requests.post(
                    f"{self.climatiq_base_url}/{endpoint}",
                    json=data,
                    headers=headers,
                    timeout=10
                )
                
                # Update rate limiting tracking
                self._update_rate_limit_tracking('climatiq')
                
                # Handle rate limit responses
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    if attempt < max_retries - 1:
                        time.sleep(retry_after)
                        continue
                    else:
                        last_error = f"Rate limit exceeded (429). Retry after {retry_after} seconds."
                        return None
                
                # Handle authentication errors
                if response.status_code == 401:
                    last_error = "Authentication failed. Please check your API key."
                    return None
                
                # Handle forbidden access
                if response.status_code == 403:
                    last_error = "Access forbidden. Please check your API permissions."
                    return None
                
                # Handle not found errors
                if response.status_code == 404:
                    last_error = f"API endpoint not found: {endpoint}"
                    return None
                
                # Handle server errors
                if response.status_code >= 500:
                    last_error = f"Server error ({response.status_code}). Service may be temporarily unavailable."
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    else:
                        return None
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                last_error = f"Request timeout (attempt {attempt + 1}/{max_retries})"
                if attempt < max_retries - 1:
                    # Exponential backoff for timeouts
                    time.sleep(2 ** attempt)
                    continue
                else:
                    return None
                    
            except requests.exceptions.ConnectionError:
                last_error = f"Connection error (attempt {attempt + 1}/{max_retries})"
                if attempt < max_retries - 1:
                    # Exponential backoff for connection errors
                    time.sleep(2 ** attempt)
                    continue
                else:
                    return None
            
            except requests.exceptions.HTTPError as e:
                last_error = f"HTTP error: {e}"
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    return None
                    
            except requests.RequestException as e:
                last_error = f"Request error: {e}"
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    return None
            
            except Exception as e:
                last_error = f"Unexpected error: {e}"
                return None
        
        # Log the last error for debugging
        if last_error:
            logging.warning(f"Climatiq API failed after {max_retries} attempts: {last_error}")
        
        return None
    
    def query_google_maps_api(self, endpoint: str, params: Dict[str, Any], max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Query Google Maps API with retry logic and comprehensive error handling"""
        if not self.google_maps_api_key:
            return None
        
        # Check rate limits before making request
        if not self._check_rate_limit('google_maps'):
            return None
        
        params['key'] = self.google_maps_api_key
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Apply rate limiting delay
                self._apply_rate_limit_delay('google_maps')
                
                response = requests.get(
                    f"{self.google_maps_base_url}/{endpoint}",
                    params=params,
                    timeout=10
                )
                
                # Update rate limiting tracking
                self._update_rate_limit_tracking('google_maps')
                
                # Handle rate limit responses
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    if attempt < max_retries - 1:
                        time.sleep(retry_after)
                        continue
                    else:
                        last_error = f"Rate limit exceeded (429). Retry after {retry_after} seconds."
                        return None
                
                # Handle authentication errors
                if response.status_code == 401:
                    last_error = "Authentication failed. Please check your Google Maps API key."
                    return None
                
                # Handle forbidden access
                if response.status_code == 403:
                    last_error = "Access forbidden. Please check your Google Maps API permissions and billing."
                    return None
                
                # Handle server errors
                if response.status_code >= 500:
                    last_error = f"Server error ({response.status_code}). Google Maps service may be temporarily unavailable."
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    else:
                        return None
                
                response.raise_for_status()
                api_response = response.json()
                
                # Check for Google Maps specific error statuses
                if 'status' in api_response:
                    status = api_response.get('status')
                    if status == 'REQUEST_DENIED':
                        last_error = "Request denied. Please check your API key and permissions."
                        return None
                    elif status == 'OVER_QUERY_LIMIT':
                        last_error = "Query limit exceeded. Please check your API quota."
                        return None
                    elif status == 'INVALID_REQUEST':
                        last_error = "Invalid request parameters."
                        return None
                    elif status == 'ZERO_RESULTS':
                        # This is not an error, just no results found
                        return api_response
                    elif status != 'OK':
                        last_error = f"API returned status: {status}"
                        return None
                
                return api_response
                
            except requests.exceptions.Timeout:
                last_error = f"Request timeout (attempt {attempt + 1}/{max_retries})"
                if attempt < max_retries - 1:
                    # Exponential backoff for timeouts
                    time.sleep(2 ** attempt)
                    continue
                else:
                    return None
                    
            except requests.exceptions.ConnectionError:
                last_error = f"Connection error (attempt {attempt + 1}/{max_retries})"
                if attempt < max_retries - 1:
                    # Exponential backoff for connection errors
                    time.sleep(2 ** attempt)
                    continue
                else:
                    return None
            
            except requests.exceptions.HTTPError as e:
                last_error = f"HTTP error: {e}"
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    return None
                    
            except requests.RequestException as e:
                last_error = f"Request error: {e}"
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    return None
            
            except Exception as e:
                last_error = f"Unexpected error: {e}"
                return None
        
        # Log the last error for debugging
        if last_error:
            logging.warning(f"Google Maps API failed after {max_retries} attempts: {last_error}")
        
        return None
    
    def get_emission_factor_with_fallback(self, transport_mode: str, distance_km: float = None) -> float:
        """Get emission factor from API with fallback to static data"""
        # Try to get from Climatiq API first
        api_factor = self._get_climatiq_emission_factor(transport_mode, distance_km)
        
        if api_factor is not None:
            return api_factor
        
        # Fallback to static emission factors
        return self.static_emission_factors.get(transport_mode, 0.0)
    
    def _get_climatiq_emission_factor(self, transport_mode: str, distance_km: float = None) -> Optional[float]:
        """Query Climatiq API for emission factors"""
        # Map transport modes to Climatiq activity IDs
        activity_mapping = {
            'Flight': 'passenger_flight-route_type_domestic-aircraft_type_na-distance_na-class_na-rf_na',
            'Train': 'passenger_train-route_type_national_rail-fuel_source_na',
            'Car': 'passenger_vehicle-vehicle_type_car-fuel_source_petrol-engine_size_na-vehicle_age_na-vehicle_weight_na',
            'Bus': 'passenger_vehicle-vehicle_type_bus-fuel_source_diesel-engine_size_na-vehicle_age_na-vehicle_weight_na',
            'Hotel': 'accommodation-type_hotel'
        }
        
        activity_id = activity_mapping.get(transport_mode)
        if not activity_id:
            return None
        
        # Prepare API request data
        request_data = {
            'emission_factor': {
                'activity_id': activity_id,
                'source': 'DEFRA',
                'region': 'IN',  # India
                'year': 2023
            }
        }
        
        # Add distance for transport modes if provided
        if distance_km and transport_mode != 'Hotel':
            request_data['parameters'] = {
                'distance': distance_km,
                'distance_unit': 'km'
            }
        
        try:
            response = self.query_climatiq_api('estimate', request_data)
            if response and 'co2e' in response:
                return response['co2e']
        except Exception:
            pass
        
        return None
    
    def _check_rate_limit(self, api_name: str) -> bool:
        """Check if we're within rate limits for the specified API"""
        now = datetime.now()
        
        # Reset counters if window has passed
        if now - self._rate_limit_window_start > timedelta(minutes=1):
            self._climatiq_request_count = 0
            self._google_maps_request_count = 0
            self._rate_limit_window_start = now
        
        if api_name == 'climatiq':
            return self._climatiq_request_count < self.climatiq_rate_limit
        elif api_name == 'google_maps':
            return self._google_maps_request_count < self.google_maps_rate_limit
        
        return False
    
    def _apply_rate_limit_delay(self, api_name: str) -> None:
        """Apply appropriate delay between requests"""
        now = datetime.now()
        
        if api_name == 'climatiq' and self._last_climatiq_request:
            elapsed = (now - self._last_climatiq_request).total_seconds()
            if elapsed < 1.0:  # Minimum 1 second between requests
                time.sleep(1.0 - elapsed)
        elif api_name == 'google_maps' and self._last_google_maps_request:
            elapsed = (now - self._last_google_maps_request).total_seconds()
            if elapsed < 0.6:  # Minimum 0.6 seconds between requests
                time.sleep(0.6 - elapsed)
    
    def _update_rate_limit_tracking(self, api_name: str) -> None:
        """Update rate limiting tracking after successful request"""
        now = datetime.now()
        
        if api_name == 'climatiq':
            self._last_climatiq_request = now
            self._climatiq_request_count += 1
        elif api_name == 'google_maps':
            self._last_google_maps_request = now
            self._google_maps_request_count += 1
    
    def handle_api_errors(self, response: Optional[Dict[str, Any]], api_name: str = "Unknown") -> Dict[str, Any]:
        """Enhanced API error handling with detailed error information"""
        error_info = {
            'has_error': False,
            'error_type': None,
            'error_message': None,
            'user_message': None,
            'retry_recommended': False,
            'fallback_available': True
        }
        
        if response is None:
            error_info.update({
                'has_error': True,
                'error_type': 'no_response',
                'error_message': f'{api_name} API returned no response',
                'user_message': f'{api_name} service is temporarily unavailable. Using fallback data.',
                'retry_recommended': True,
                'fallback_available': True
            })
            return error_info
        
        # Check for common error indicators
        if 'error' in response:
            error_details = response.get('error', {})
            if isinstance(error_details, dict):
                error_message = error_details.get('message', 'Unknown error')
                error_code = error_details.get('code', 'unknown')
            else:
                error_message = str(error_details)
                error_code = 'unknown'
            
            error_info.update({
                'has_error': True,
                'error_type': 'api_error',
                'error_message': f'{api_name} API error: {error_message} (Code: {error_code})',
                'user_message': f'{api_name} service encountered an error. Using fallback data.',
                'retry_recommended': error_code not in ['invalid_key', 'forbidden'],
                'fallback_available': True
            })
            return error_info
        
        # Check Google Maps specific error statuses
        if 'status' in response:
            status = response.get('status')
            error_statuses = {
                'REQUEST_DENIED': {
                    'message': 'API request was denied. Please check your API key and permissions.',
                    'retry': False
                },
                'OVER_QUERY_LIMIT': {
                    'message': 'API quota exceeded. Please check your usage limits.',
                    'retry': True
                },
                'INVALID_REQUEST': {
                    'message': 'Invalid request parameters provided.',
                    'retry': False
                },
                'UNKNOWN_ERROR': {
                    'message': 'Unknown server error occurred.',
                    'retry': True
                }
            }
            
            if status in error_statuses:
                error_details = error_statuses[status]
                error_info.update({
                    'has_error': True,
                    'error_type': 'status_error',
                    'error_message': f'{api_name} API status: {status}',
                    'user_message': error_details['message'] + ' Using fallback data.',
                    'retry_recommended': error_details['retry'],
                    'fallback_available': True
                })
                return error_info
            
            # ZERO_RESULTS is not an error, just no data
            if status == 'ZERO_RESULTS':
                return error_info  # No error
        
        return error_info  # No error detected
    
    def get_api_status(self) -> Dict[str, Dict[str, Any]]:
        """Get current status of all APIs with detailed information"""
        status_info = {
            'climatiq': {
                'configured': bool(self.climatiq_api_key),
                'available': False,
                'last_error': None,
                'fallback_active': False
            },
            'google_maps': {
                'configured': bool(self.google_maps_api_key),
                'available': False,
                'last_error': None,
                'fallback_active': False
            }
        }
        
        # Test Climatiq API if configured
        if self.climatiq_api_key:
            try:
                # Simple test request
                test_response = self.query_climatiq_api('estimate', {
                    'emission_factor': {
                        'activity_id': 'passenger_flight-route_type_domestic-aircraft_type_na-distance_na-class_na-rf_na',
                        'source': 'DEFRA',
                        'region': 'IN',
                        'year': 2023
                    },
                    'parameters': {
                        'distance': 100,
                        'distance_unit': 'km'
                    }
                })
                
                error_info = self.handle_api_errors(test_response, 'Climatiq')
                status_info['climatiq']['available'] = not error_info['has_error']
                if error_info['has_error']:
                    status_info['climatiq']['last_error'] = error_info['error_message']
                    status_info['climatiq']['fallback_active'] = True
                    
            except Exception as e:
                status_info['climatiq']['last_error'] = str(e)
                status_info['climatiq']['fallback_active'] = True
        
        # Test Google Maps API if configured
        if self.google_maps_api_key:
            try:
                # Simple test request
                test_response = self.query_google_maps_api('directions/json', {
                    'origin': 'Delhi',
                    'destination': 'Mumbai',
                    'mode': 'driving'
                })
                
                error_info = self.handle_api_errors(test_response, 'Google Maps')
                status_info['google_maps']['available'] = not error_info['has_error']
                if error_info['has_error']:
                    status_info['google_maps']['last_error'] = error_info['error_message']
                    status_info['google_maps']['fallback_active'] = True
                    
            except Exception as e:
                status_info['google_maps']['last_error'] = str(e)
                status_info['google_maps']['fallback_active'] = True
        
        return status_info
    
    def validate_api_configuration(self) -> Dict[str, Any]:
        """Validate API configuration and return detailed status"""
        config_status = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Check Climatiq API configuration
        if not self.climatiq_api_key:
            config_status['warnings'].append("Climatiq API key not configured - using static emission factors")
            config_status['recommendations'].append("Set CLIMATIQ_API_KEY environment variable for real-time emission data")
        elif len(self.climatiq_api_key) < 10:
            config_status['errors'].append("Climatiq API key appears to be invalid (too short)")
            config_status['is_valid'] = False
        
        # Check Google Maps API configuration
        if not self.google_maps_api_key:
            config_status['warnings'].append("Google Maps API key not configured - using fallback route estimation")
            config_status['recommendations'].append("Set GOOGLE_MAPS_API_KEY environment variable for detailed route information")
        elif len(self.google_maps_api_key) < 10:
            config_status['errors'].append("Google Maps API key appears to be invalid (too short)")
            config_status['is_valid'] = False
        
        # Check for common configuration issues
        if self.climatiq_api_key and self.climatiq_api_key.startswith('sk-'):
            config_status['warnings'].append("Climatiq API key format may be incorrect (should not start with 'sk-')")
        
        if self.google_maps_api_key and not self.google_maps_api_key.startswith('AIza'):
            config_status['warnings'].append("Google Maps API key format may be incorrect (should start with 'AIza')")
        
        return config_status
    
    def manage_rate_limits(self, api_name: str) -> None:
        """Implement rate limiting management"""
        # This method is kept for backward compatibility
        # Rate limiting is now handled automatically in query methods
        pass
    
    def fetch_alternative_routes(self, origin: str, destination: str, 
                               travel_modes: Optional[List[str]] = None) -> Dict[str, Any]:
        """Fetch alternative routes for different transportation modes from Google Maps API"""
        if travel_modes is None:
            travel_modes = ['driving', 'transit']
        
        # Map our internal modes to Google Maps travel modes
        mode_mapping = {
            'Car': 'driving',
            'Bus': 'transit',
            'Train': 'transit',
            'Flight': None  # Flights not supported by Directions API
        }
        
        routes_data = {}
        
        for mode in travel_modes:
            google_mode = mode_mapping.get(mode, mode.lower())
            
            # Skip unsupported modes
            if google_mode is None:
                continue
            
            # Prepare API parameters
            params = {
                'origin': origin,
                'destination': destination,
                'mode': google_mode,
                'alternatives': 'true',
                'units': 'metric'
            }
            
            # Add transit-specific parameters
            if google_mode == 'transit':
                params['transit_mode'] = 'bus|rail'
            
            try:
                response = self.query_google_maps_api('directions/json', params)
                
                if response and not self.handle_api_errors(response):
                    routes_data[mode] = self._process_directions_response(response, mode)
                else:
                    # Fallback to distance-based estimation
                    routes_data[mode] = self._create_fallback_route(origin, destination, mode)
                    
            except Exception as e:
                # Create fallback route on any error
                routes_data[mode] = self._create_fallback_route(origin, destination, mode)
        
        return routes_data
    
    def _process_directions_response(self, response: Dict[str, Any], mode: str) -> List[Dict[str, Any]]:
        """Process Google Maps Directions API response into route data"""
        processed_routes = []
        
        if 'routes' not in response or not response['routes']:
            return processed_routes
        
        for route in response['routes']:
            try:
                # Extract route information
                leg = route['legs'][0] if route['legs'] else {}
                
                route_data = {
                    'mode': mode,
                    'distance_km': leg.get('distance', {}).get('value', 0) / 1000.0,
                    'duration_hours': leg.get('duration', {}).get('value', 0) / 3600.0,
                    'start_address': leg.get('start_address', ''),
                    'end_address': leg.get('end_address', ''),
                    'steps': self._extract_route_steps(leg.get('steps', [])),
                    'polyline': route.get('overview_polyline', {}).get('points', ''),
                    'bounds': route.get('bounds', {}),
                    'warnings': route.get('warnings', []),
                    'copyrights': route.get('copyrights', '')
                }
                
                # Add transit-specific information
                if mode in ['Bus', 'Train'] and 'transit_details' in str(leg):
                    route_data['transit_details'] = self._extract_transit_details(leg.get('steps', []))
                
                processed_routes.append(route_data)
                
            except Exception as e:
                # Skip malformed route data
                continue
        
        return processed_routes
    
    def _extract_route_steps(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract simplified step information from route"""
        simplified_steps = []
        
        for step in steps:
            try:
                step_data = {
                    'distance_km': step.get('distance', {}).get('value', 0) / 1000.0,
                    'duration_hours': step.get('duration', {}).get('value', 0) / 3600.0,
                    'instructions': step.get('html_instructions', ''),
                    'travel_mode': step.get('travel_mode', ''),
                    'start_location': step.get('start_location', {}),
                    'end_location': step.get('end_location', {})
                }
                
                simplified_steps.append(step_data)
                
            except Exception:
                continue
        
        return simplified_steps
    
    def _extract_transit_details(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract transit-specific details from route steps"""
        transit_details = []
        
        for step in steps:
            if step.get('travel_mode') == 'TRANSIT' and 'transit_details' in step:
                try:
                    transit_info = step['transit_details']
                    detail = {
                        'line_name': transit_info.get('line', {}).get('name', ''),
                        'vehicle_type': transit_info.get('line', {}).get('vehicle', {}).get('type', ''),
                        'departure_stop': transit_info.get('departure_stop', {}).get('name', ''),
                        'arrival_stop': transit_info.get('arrival_stop', {}).get('name', ''),
                        'num_stops': transit_info.get('num_stops', 0)
                    }
                    transit_details.append(detail)
                    
                except Exception:
                    continue
        
        return transit_details
    
    def _create_fallback_route(self, origin: str, destination: str, mode: str) -> List[Dict[str, Any]]:
        """Create fallback route data when API is unavailable"""
        # Estimate distance using geographic data if available
        from .geographic_data import GeographicDataManager
        
        try:
            geo_manager = GeographicDataManager()
            origin_coords = geo_manager.get_city_coordinates(origin)
            dest_coords = geo_manager.get_city_coordinates(destination)
            
            if origin_coords and dest_coords:
                distance_km = geo_manager.calculate_geodesic_distance(
                    origin_coords['latitude'], origin_coords['longitude'],
                    dest_coords['latitude'], dest_coords['longitude']
                )
            else:
                # Default fallback distance
                distance_km = 500.0
            
            # Estimate duration based on mode and distance
            speed_estimates = {
                'Car': 60.0,    # km/h average including stops
                'Bus': 45.0,    # km/h average including stops
                'Train': 80.0,  # km/h average for Indian trains
                'Flight': 500.0 # km/h average including airport time
            }
            
            speed = speed_estimates.get(mode, 50.0)
            duration_hours = distance_km / speed
            
            fallback_route = {
                'mode': mode,
                'distance_km': round(distance_km, 2),
                'duration_hours': round(duration_hours, 2),
                'start_address': origin,
                'end_address': destination,
                'steps': [],
                'polyline': '',
                'bounds': {},
                'warnings': ['Route calculated using fallback estimation'],
                'copyrights': 'Fallback route estimation',
                'is_fallback': True
            }
            
            return [fallback_route]
            
        except Exception:
            # Ultimate fallback with default values
            return [{
                'mode': mode,
                'distance_km': 500.0,
                'duration_hours': 8.0,
                'start_address': origin,
                'end_address': destination,
                'steps': [],
                'polyline': '',
                'bounds': {},
                'warnings': ['Route calculated using default estimation'],
                'copyrights': 'Default route estimation',
                'is_fallback': True
            }]