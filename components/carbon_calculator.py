"""
Carbon calculation engine for EcoTrip Planner

Computes CO₂ emissions for transportation and accommodation with API integration
and fallback mechanisms using static emission factors.
"""

from typing import Dict, Any, Optional
from .ml_emissions_model import MLEmissionsPredictor
from .models import TripData, EmissionsResult
from datetime import datetime


class CarbonCalculator:
    """Engine for calculating carbon emissions from travel and accommodation"""
    
    def __init__(self):
        self.ml_predictor = MLEmissionsPredictor()
    
    def calculate_transport_emissions(self, trip_data: TripData, distance_km: float) -> Dict[str, float]:
        """Calculate emissions for transportation modes with comprehensive error handling"""
        transport_emissions = {}
        calculation_errors = []
        
        try:
            # Validate inputs
            if not self.validate_calculation_inputs(trip_data, distance_km):
                raise ValueError("Invalid calculation inputs provided")
            
            for mode in trip_data.travel_modes:
                try:
                    # Get emission factor from ML model
                    emission_factor = self.ml_predictor.predict_emission_factor(mode, distance_km, trip_data.num_travelers)
                    
                    if emission_factor > 0:
                        # Calculate emissions: distance * emission_factor * number_of_travelers
                        emissions = distance_km * emission_factor * trip_data.num_travelers
                        transport_emissions[mode] = round(emissions, 3)
                    else:
                        calculation_errors.append(f"No emission factor available for {mode}")
                        
                except Exception as e:
                    calculation_errors.append(f"Error calculating emissions for {mode}: {str(e)}")
                    continue
            
            # If no successful calculations, raise an error
            if not transport_emissions and calculation_errors:
                raise ValueError(f"Failed to calculate emissions for any transport mode: {'; '.join(calculation_errors)}")
            
        except Exception as e:
            # Log error and return empty result
            calculation_errors.append(f"Transport emissions calculation failed: {str(e)}")
            
        # Store any errors for later reporting
        if hasattr(self, '_calculation_errors'):
            self._calculation_errors.extend(calculation_errors)
        else:
            self._calculation_errors = calculation_errors
        
        return transport_emissions
    
    def calculate_accommodation_emissions(self, trip_data: TripData) -> float:
        """Calculate emissions for hotel accommodation with error handling"""
        try:
            if trip_data.hotel_nights <= 0:
                return 0.0
            
            # Validate inputs
            if trip_data.num_travelers <= 0:
                raise ValueError("Number of travelers must be positive")
            
            if trip_data.hotel_nights > 365:
                raise ValueError("Hotel nights cannot exceed 365")
            
            # Get emission factor for hotel accommodation from ML model
            emissions = self.ml_predictor.predict_accommodation_emissions(
                trip_data.hotel_nights, 
                trip_data.num_travelers
            )
            
            if emissions > 0:
                return round(emissions, 3)
            else:
                raise ValueError("No emission factor available for hotel accommodation")
        
        except Exception as e:
            # Log error and return zero
            if hasattr(self, '_calculation_errors'):
                self._calculation_errors.append(f"Accommodation emissions calculation failed: {str(e)}")
            else:
                self._calculation_errors = [f"Accommodation emissions calculation failed: {str(e)}"]
            return 0.0
    
    def calculate_total_emissions(self, trip_data: TripData, distance_km: float) -> EmissionsResult:
        """Calculate total emissions for the entire trip with comprehensive error handling"""
        # Initialize error tracking
        self._calculation_errors = []
        
        try:
            # Validate inputs first
            if not self.validate_calculation_inputs(trip_data, distance_km):
                raise ValueError("Invalid inputs for emissions calculation")
            
            # Calculate transport emissions for all selected modes
            transport_emissions = self.calculate_transport_emissions(trip_data, distance_km)
            
            # Calculate accommodation emissions
            accommodation_emissions = self.calculate_accommodation_emissions(trip_data)
            
            # Check if we have any valid calculations
            if not transport_emissions and accommodation_emissions == 0.0:
                raise ValueError("No valid emissions could be calculated")
            
            # Aggregate total emissions
            result = self.aggregate_total_emissions(transport_emissions, accommodation_emissions, trip_data.num_travelers)
            
            # Add error information to result if any errors occurred
            if self._calculation_errors:
                result.calculation_warnings = self._calculation_errors
            
            return result
            
        except Exception as e:
            # Return a minimal result with error information
            error_message = f"Emissions calculation failed: {str(e)}"
            self._calculation_errors.append(error_message)
            
            return EmissionsResult(
                total_co2e_kg=0.0,
                transport_emissions={},
                accommodation_emissions=0.0,
                per_person_emissions=0.0,
                calculation_timestamp=datetime.now(),
                calculation_warnings=self._calculation_errors
            )
    
    def get_emission_factors(self, transport_mode: str, distance_km: Optional[float] = None) -> Optional[float]:
        """Retrieve emission factors from ML model"""
        return self.ml_predictor.predict_emission_factor(transport_mode, distance_km)
    
    def aggregate_total_emissions(self, transport_emissions: Dict[str, float], 
                                accommodation_emissions: float, num_travelers: int = 1) -> EmissionsResult:
        """Combine all emission sources into total result"""
        total_transport = sum(transport_emissions.values())
        total_emissions = total_transport + accommodation_emissions
        
        # Calculate per-person emissions
        per_person_emissions = total_emissions / max(1, num_travelers)
        
        return EmissionsResult(
            total_co2e_kg=round(total_emissions, 3),
            transport_emissions=transport_emissions,
            accommodation_emissions=round(accommodation_emissions, 3),
            per_person_emissions=round(per_person_emissions, 3),
            calculation_timestamp=datetime.now()
        )
    
    def calculate_emissions_by_mode(self, mode: str, distance_km: float, num_travelers: int) -> float:
        """Calculate emissions for a specific transport mode using ML model"""
        emissions = self.ml_predictor.predict_total_emissions(mode, distance_km, num_travelers)
        return round(emissions, 3)
    
    def calculate_accommodation_emissions_per_night(self, num_travelers: int) -> float:
        """Calculate accommodation emissions per night using ML model"""
        emissions_per_night = self.ml_predictor.predict_accommodation_emissions(1, num_travelers)
        return round(emissions_per_night, 3)
    
    def validate_calculation_inputs(self, trip_data: TripData, distance_km: float) -> bool:
        """Validate inputs for emission calculations with detailed error reporting"""
        validation_errors = []
        
        try:
            # Check trip data is valid
            if not trip_data.validate():
                validation_errors.append("Trip data validation failed")
            
            # Check distance is non-negative and reasonable
            if distance_km < 0:
                validation_errors.append("Distance cannot be negative")
            elif distance_km > 50000:  # More than halfway around Earth
                validation_errors.append("Distance appears unreasonably large (>50,000 km)")
            
            # Check that we have either travel modes or hotel nights (or both)
            if not trip_data.travel_modes and trip_data.hotel_nights <= 0:
                validation_errors.append("At least one travel mode must be selected or hotel nights must be greater than 0")
            
            # Validate travel modes are supported
            supported_modes = ['Flight', 'Train', 'Car', 'Bus']
            invalid_modes = [mode for mode in trip_data.travel_modes if mode not in supported_modes]
            if invalid_modes:
                validation_errors.append(f"Unsupported travel modes: {', '.join(invalid_modes)}")
            
            # Check number of travelers is reasonable
            if trip_data.num_travelers <= 0:
                validation_errors.append("Number of travelers must be positive")
            elif trip_data.num_travelers > 100:
                validation_errors.append("Number of travelers exceeds reasonable limit (100)")
            
            # Check hotel nights is reasonable
            if trip_data.hotel_nights < 0:
                validation_errors.append("Hotel nights cannot be negative")
            elif trip_data.hotel_nights > 365:
                validation_errors.append("Hotel nights exceeds reasonable limit (365)")
            
        except Exception as e:
            validation_errors.append(f"Validation error: {str(e)}")
        
        # Store validation errors
        if validation_errors:
            if hasattr(self, '_calculation_errors'):
                self._calculation_errors.extend(validation_errors)
            else:
                self._calculation_errors = validation_errors
            return False
        
        return True
    
    def get_calculation_status(self) -> Dict[str, Any]:
        """Get status of the last calculation including any errors or warnings"""
        model_info = self.ml_predictor.get_model_info()
        return {
            'has_errors': bool(getattr(self, '_calculation_errors', [])),
            'errors': getattr(self, '_calculation_errors', []),
            'model_info': model_info,
            'calculation_method': 'ml_based',
            'api_dependent': False
        }
    
    def clear_calculation_errors(self) -> None:
        """Clear any stored calculation errors"""
        self._calculation_errors = []