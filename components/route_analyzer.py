"""
Route analyzer and cost estimator for EcoTrip Planner

Processes route data to extract time, distance, and mode information,
calculates emissions for alternatives, and estimates costs with savings analysis.
"""

from typing import Dict, List, Any, Optional
from .ml_route_predictor import MLRoutePredictor
from .carbon_calculator import CarbonCalculator
from .models import TripData, AlternativeRoute
import logging


class RouteAnalyzer:
    """Processes route data and analyzes alternatives"""
    
    def __init__(self):
        self.ml_route_predictor = MLRoutePredictor()
        self.carbon_calculator = CarbonCalculator()
        
        # Cost factors per transportation mode (INR per km per person)
        self.cost_factors = {
            'Flight': 8.0,    # INR per km (domestic flights in India)
            'Train': 1.2,     # INR per km (AC 3-tier average)
            'Car': 6.0,       # INR per km (fuel + tolls + wear)
            'Bus': 2.5        # INR per km (AC bus services)
        }
        
        # Base costs (fixed costs regardless of distance)
        self.base_costs = {
            'Flight': 500.0,  # Airport taxes, convenience fees
            'Train': 50.0,    # Reservation fees
            'Car': 0.0,       # No base cost for personal vehicle
            'Bus': 25.0       # Booking fees
        }
    
    def generate_alternatives(self, origin_city: str, destination_city: str, 
                            selected_modes: List[str], baseline_emissions: float) -> List[Dict[str, Any]]:
        """Generate alternative routes for different transportation modes using ML prediction"""
        try:
            # Use ML route predictor to get route predictions
            predicted_routes = self.ml_route_predictor.predict_alternative_routes(
                origin_city, destination_city
            )
            
            if not predicted_routes:
                return []
            
            alternatives = []
            
            # Generate alternatives for all predicted routes
            for route_prediction in predicted_routes:
                try:
                    mode = route_prediction.get('mode')
                    if not mode:
                        continue
                    
                    distance_km = route_prediction.get('distance_km', 0.0)
                    duration_hours = route_prediction.get('duration_hours', 0.0)
                    
                    if distance_km <= 0:
                        continue
                    
                    # Calculate emissions for this mode
                    emissions_kg = self.carbon_calculator.calculate_emissions_by_mode(mode, distance_km, 1)
                    
                    # Estimate costs for this mode
                    estimated_cost = self.estimate_costs(mode, distance_km, 1)
                    
                    # Calculate savings relative to baseline
                    emissions_savings = baseline_emissions - emissions_kg
                    
                    # Create alternative data
                    alternative = {
                        'transport_mode': mode,
                        'duration_hours': round(duration_hours, 2),
                        'distance_km': round(distance_km, 2),
                        'co2e_emissions_kg': round(emissions_kg, 3),
                        'estimated_cost_inr': round(estimated_cost, 2),
                        'emissions_savings_kg': round(emissions_savings, 3),
                        'cost_difference_inr': 0.0,  # Will be calculated if baseline cost is provided
                        'route_details': {
                            'start_address': origin_city,
                            'end_address': destination_city,
                            'is_predicted': True,
                            'calculation_method': 'ml_prediction',
                            'prediction_method': route_prediction.get('prediction_method', 'ml_geographic')
                        }
                    }
                    
                    alternatives.append(alternative)
                    
                except Exception as e:
                    mode_name = route_prediction.get('mode', 'unknown') if 'route_prediction' in locals() else 'unknown'
                    logging.warning(f"Failed to generate alternative for mode {mode_name}: {e}")
                    continue
            
            # Sort alternatives by emissions (lowest first)
            alternatives.sort(key=lambda x: x['co2e_emissions_kg'])
            
            return alternatives
            
        except Exception as e:
            logging.error(f"Failed to generate alternatives: {e}")
            return []
    
    def _estimate_duration(self, mode: str, distance_km: float) -> float:
        """Estimate travel duration based on mode and distance using ML predictor"""
        # Use ML route predictor for duration estimation
        # This is a fallback method - normally duration comes from route prediction
        try:
            # Get speed and buffer from ML route predictor
            speed = self.ml_route_predictor.mode_speeds.get(mode, 50.0)
            buffer = self.ml_route_predictor.mode_buffers.get(mode, 0.5)
            
            # Calculate travel time: distance / speed
            travel_time = distance_km / max(speed, 1.0)
            total_time = travel_time + buffer
            
            return max(total_time, 0.5)  # Minimum 30 minutes
        except Exception as e:
            # Fallback to original calculation
            average_speeds = {
                'Flight': 500.0,
                'Train': 60.0,
                'Car': 50.0,
                'Bus': 45.0
            }
            speed = average_speeds.get(mode, 50.0)
            buffer_hours = {
                'Flight': 3.0,
                'Train': 1.0,
                'Car': 0.5,
                'Bus': 1.0
            }
            travel_time = distance_km / speed
            total_time = travel_time + buffer_hours.get(mode, 0.5)
            return max(total_time, 0.5)
    
    def process_route_data(self, routes_data: Dict[str, Any], trip_data: TripData) -> List[AlternativeRoute]:
        """Process route data to extract time, distance, and mode information"""
        alternatives = []
        
        for mode, route_list in routes_data.items():
            if not route_list:
                continue
            
            # Process each route for this mode (usually just one, but API can return alternatives)
            for route_info in route_list:
                try:
                    alternative = self._create_alternative_route(route_info, mode, trip_data)
                    if alternative:
                        alternatives.append(alternative)
                        
                except Exception as e:
                    logging.warning(f"Failed to process route for mode {mode}: {e}")
                    continue
        
        return alternatives
    
    def _create_alternative_route(self, route_info: Dict[str, Any], mode: str, trip_data: TripData) -> Optional[AlternativeRoute]:
        """Create AlternativeRoute object from route information"""
        try:
            # Extract basic route information
            distance_km = route_info.get('distance_km', 0.0)
            duration_hours = route_info.get('duration_hours', 0.0)
            
            # Calculate emissions for this alternative
            emissions_kg = self.calculate_emissions_for_alternative(mode, distance_km, trip_data.num_travelers)
            
            # Estimate costs for this alternative
            estimated_cost = self.estimate_costs(mode, distance_km, trip_data.num_travelers)
            
            # Create route details dictionary
            route_details = {
                'start_address': route_info.get('start_address', ''),
                'end_address': route_info.get('end_address', ''),
                'steps': route_info.get('steps', []),
                'polyline': route_info.get('polyline', ''),
                'bounds': route_info.get('bounds', {}),
                'warnings': route_info.get('warnings', []),
                'copyrights': route_info.get('copyrights', ''),
                'is_fallback': route_info.get('is_fallback', False)
            }
            
            # Add transit details if available
            if 'transit_details' in route_info:
                route_details['transit_details'] = route_info['transit_details']
            
            # Create alternative route (savings will be calculated later)
            alternative = AlternativeRoute(
                transport_mode=mode,
                duration_hours=round(duration_hours, 2),
                distance_km=round(distance_km, 2),
                co2e_emissions_kg=round(emissions_kg, 3),
                estimated_cost_inr=round(estimated_cost, 2),
                emissions_savings_kg=0.0,  # Will be calculated when baseline is known
                cost_difference_inr=0.0,   # Will be calculated when baseline is known
                route_details=route_details
            )
            
            return alternative
            
        except Exception as e:
            logging.error(f"Error creating alternative route for mode {mode}: {e}")
            return None
    
    def calculate_emissions_for_alternative(self, mode: str, distance_km: float, num_travelers: int) -> float:
        """Calculate emissions for each alternative using carbon calculator"""
        return self.carbon_calculator.calculate_emissions_by_mode(mode, distance_km, num_travelers)
    
    def estimate_costs(self, mode: str, distance_km: float, num_travelers: int) -> float:
        """Estimate costs using predefined cost factors per transportation mode"""
        # Get cost factor for this mode
        cost_per_km = self.cost_factors.get(mode, 0.0)
        base_cost = self.base_costs.get(mode, 0.0)
        
        # Calculate total cost: (base_cost + distance_cost) * num_travelers
        distance_cost = distance_km * cost_per_km
        total_cost_per_person = base_cost + distance_cost
        total_cost = total_cost_per_person * num_travelers
        
        return total_cost
    
    def compute_savings_relative_to_baseline(self, alternatives: List[AlternativeRoute], 
                                           baseline_emissions: float, baseline_cost: float) -> List[AlternativeRoute]:
        """Compute emission and cost savings relative to baseline"""
        updated_alternatives = []
        
        for alternative in alternatives:
            # Calculate emissions savings (positive means savings, negative means increase)
            emissions_savings = baseline_emissions - alternative.co2e_emissions_kg
            
            # Calculate cost difference (positive means more expensive, negative means cheaper)
            cost_difference = alternative.estimated_cost_inr - baseline_cost
            
            # Update the alternative with savings calculations
            updated_alternative = AlternativeRoute(
                transport_mode=alternative.transport_mode,
                duration_hours=alternative.duration_hours,
                distance_km=alternative.distance_km,
                co2e_emissions_kg=alternative.co2e_emissions_kg,
                estimated_cost_inr=alternative.estimated_cost_inr,
                emissions_savings_kg=round(emissions_savings, 3),
                cost_difference_inr=round(cost_difference, 2),
                route_details=alternative.route_details
            )
            
            updated_alternatives.append(updated_alternative)
        
        return updated_alternatives
    
    def rank_alternatives_by_emissions(self, alternatives: List[AlternativeRoute]) -> List[AlternativeRoute]:
        """Rank alternatives by emissions (lowest first)"""
        return sorted(alternatives, key=lambda x: x.co2e_emissions_kg)
    
    def rank_alternatives_by_cost(self, alternatives: List[AlternativeRoute]) -> List[AlternativeRoute]:
        """Rank alternatives by cost (lowest first)"""
        return sorted(alternatives, key=lambda x: x.estimated_cost_inr)
    
    def rank_alternatives_by_savings(self, alternatives: List[AlternativeRoute]) -> List[AlternativeRoute]:
        """Rank alternatives by emission savings (highest savings first)"""
        return sorted(alternatives, key=lambda x: x.emissions_savings_kg, reverse=True)
    
    def filter_alternatives_by_mode(self, alternatives: List[AlternativeRoute], modes: List[str]) -> List[AlternativeRoute]:
        """Filter alternatives to include only specified modes"""
        return [alt for alt in alternatives if alt.transport_mode in modes]
    
    def get_best_alternative_by_emissions(self, alternatives: List[AlternativeRoute]) -> Optional[AlternativeRoute]:
        """Get the alternative with lowest emissions"""
        if not alternatives:
            return None
        return min(alternatives, key=lambda x: x.co2e_emissions_kg)
    
    def get_best_alternative_by_cost(self, alternatives: List[AlternativeRoute]) -> Optional[AlternativeRoute]:
        """Get the alternative with lowest cost"""
        if not alternatives:
            return None
        return min(alternatives, key=lambda x: x.estimated_cost_inr)
    
    def analyze_route_efficiency(self, alternatives: List[AlternativeRoute]) -> Dict[str, Any]:
        """Compare time, distance, and emissions across alternatives"""
        if not alternatives:
            return {}
        
        analysis = {
            'total_alternatives': len(alternatives),
            'modes_available': list(set(alt.transport_mode for alt in alternatives)),
            'emissions_range': {
                'min': min(alt.co2e_emissions_kg for alt in alternatives),
                'max': max(alt.co2e_emissions_kg for alt in alternatives),
                'avg': sum(alt.co2e_emissions_kg for alt in alternatives) / len(alternatives)
            },
            'cost_range': {
                'min': min(alt.estimated_cost_inr for alt in alternatives),
                'max': max(alt.estimated_cost_inr for alt in alternatives),
                'avg': sum(alt.estimated_cost_inr for alt in alternatives) / len(alternatives)
            },
            'duration_range': {
                'min': min(alt.duration_hours for alt in alternatives),
                'max': max(alt.duration_hours for alt in alternatives),
                'avg': sum(alt.duration_hours for alt in alternatives) / len(alternatives)
            },
            'distance_range': {
                'min': min(alt.distance_km for alt in alternatives),
                'max': max(alt.distance_km for alt in alternatives),
                'avg': sum(alt.distance_km for alt in alternatives) / len(alternatives)
            }
        }
        
        # Round averages for readability
        for category in ['emissions_range', 'cost_range', 'duration_range', 'distance_range']:
            analysis[category]['avg'] = round(analysis[category]['avg'], 2)
        
        return analysis
    
    def validate_route_data(self, route_info: Dict[str, Any]) -> bool:
        """Validate route data completeness and accuracy"""
        required_fields = ['distance_km', 'duration_hours', 'mode']
        
        # Check required fields exist
        for field in required_fields:
            if field not in route_info:
                return False
        
        # Check values are reasonable
        if route_info['distance_km'] <= 0 or route_info['duration_hours'] <= 0:
            return False
        
        # Check mode is valid
        valid_modes = {'Flight', 'Train', 'Car', 'Bus'}
        if route_info['mode'] not in valid_modes:
            return False
        
        return True


class CostEstimator:
    """Specialized component for cost estimation and analysis"""
    
    def __init__(self):
        # Detailed cost factors for different service classes
        self.detailed_cost_factors = {
            'Flight': {
                'economy': 6.0,      # INR per km
                'business': 12.0,    # INR per km
                'base_cost': 500.0   # Airport taxes, fees
            },
            'Train': {
                'sleeper': 0.8,      # INR per km
                'ac_3tier': 1.2,     # INR per km
                'ac_2tier': 1.8,     # INR per km
                'ac_1tier': 2.5,     # INR per km
                'base_cost': 50.0    # Reservation fees
            },
            'Car': {
                'petrol': 5.5,       # INR per km (fuel + maintenance)
                'diesel': 4.8,       # INR per km
                'electric': 2.0,     # INR per km
                'base_cost': 0.0     # No booking fees
            },
            'Bus': {
                'ordinary': 1.5,     # INR per km
                'ac': 2.5,           # INR per km
                'volvo': 3.5,        # INR per km
                'base_cost': 25.0    # Booking fees
            }
        }
    
    def estimate_detailed_costs(self, mode: str, distance_km: float, 
                              num_travelers: int, service_class: str = 'standard') -> Dict[str, float]:
        """Estimate costs with breakdown by service class"""
        mode_costs = self.detailed_cost_factors.get(mode, {})
        
        if not mode_costs:
            return {'total': 0.0, 'per_person': 0.0, 'base_cost': 0.0, 'distance_cost': 0.0}
        
        # Map service classes to specific cost factors
        class_mapping = {
            'Flight': {'standard': 'economy', 'premium': 'business'},
            'Train': {'standard': 'ac_3tier', 'premium': 'ac_1tier', 'budget': 'sleeper'},
            'Car': {'standard': 'petrol', 'premium': 'petrol', 'budget': 'diesel'},
            'Bus': {'standard': 'ac', 'premium': 'volvo', 'budget': 'ordinary'}
        }
        
        cost_key = class_mapping.get(mode, {}).get(service_class, 'standard')
        if isinstance(cost_key, str) and cost_key in mode_costs:
            cost_per_km = mode_costs[cost_key]
        else:
            # Fallback to first available cost
            cost_per_km = next(iter([v for k, v in mode_costs.items() if k != 'base_cost']), 0.0)
        
        base_cost = mode_costs.get('base_cost', 0.0)
        distance_cost = distance_km * cost_per_km
        cost_per_person = base_cost + distance_cost
        total_cost = cost_per_person * num_travelers
        
        return {
            'total': round(total_cost, 2),
            'per_person': round(cost_per_person, 2),
            'base_cost': round(base_cost * num_travelers, 2),
            'distance_cost': round(distance_cost * num_travelers, 2)
        }