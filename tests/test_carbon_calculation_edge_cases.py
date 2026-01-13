"""
Unit tests for carbon calculation edge cases

Tests specific edge cases and boundary conditions for carbon emissions calculations.
Requirements: 2.3, 2.4, 2.5
"""

import pytest
from datetime import date, timedelta
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the path so we can import components
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.models import TripData
from components.carbon_calculator import CarbonCalculator


class TestCarbonCalculationEdgeCases:
    """Unit tests for carbon calculation edge cases"""
    
    def setup_method(self):
        """Set up test environment"""
        self.calculator = CarbonCalculator()
    
    def test_zero_distance_calculations(self):
        """Test emissions calculation with zero distance"""
        # Create trip data for same origin and destination (zero distance)
        trip_data = TripData(
            origin_city="Delhi",
            destination_city="Delhi",
            outbound_date=date.today(),
            return_date=None,
            travel_modes=['Car'],
            num_travelers=2,
            hotel_nights=3
        )
        
        # Mock API to return emission factors
        with patch.object(self.calculator.api_client, 'get_emission_factor_with_fallback') as mock_factor:
            mock_factor.return_value = 0.1
            
            # Calculate with zero distance
            result = self.calculator.calculate_total_emissions(trip_data, 0.0)
            
            # Transport emissions should be zero for zero distance
            assert result.transport_emissions['Car'] == 0.0
            
            # Accommodation emissions should still be calculated
            assert result.accommodation_emissions > 0.0
            
            # Total should equal accommodation only
            assert result.total_co2e_kg == result.accommodation_emissions
    
    def test_maximum_traveler_limits(self):
        """Test emissions calculation with maximum number of travelers"""
        # Create trip data with maximum travelers (edge case)
        trip_data = TripData(
            origin_city="Mumbai",
            destination_city="Chennai",
            outbound_date=date.today(),
            return_date=None,
            travel_modes=['Flight', 'Train'],
            num_travelers=100,  # Large number of travelers
            hotel_nights=5
        )
        
        distance_km = 1000.0
        
        # Mock API to return emission factors
        with patch.object(self.calculator.api_client, 'get_emission_factor_with_fallback') as mock_factor:
            mock_factor.return_value = 0.2
            
            result = self.calculator.calculate_total_emissions(trip_data, distance_km)
            
            # Emissions should scale correctly with large number of travelers
            expected_transport_per_mode = distance_km * 0.2 * 100  # 20,000 kg CO2e per mode
            expected_accommodation = 5 * 0.2 * 100  # 100 kg CO2e
            
            assert result.transport_emissions['Flight'] == expected_transport_per_mode
            assert result.transport_emissions['Train'] == expected_transport_per_mode
            assert result.accommodation_emissions == expected_accommodation
            
            # Per-person emissions should be total divided by travelers
            expected_per_person = result.total_co2e_kg / 100
            assert result.per_person_emissions == expected_per_person
    
    def test_accommodation_only_trips(self):
        """Test emissions calculation for accommodation-only trips (no transport)"""
        # Create trip data with no travel modes (accommodation only)
        trip_data = TripData(
            origin_city="Goa",
            destination_city="Goa",
            outbound_date=date.today(),
            return_date=date.today() + timedelta(days=7),
            travel_modes=[],  # No transport modes
            num_travelers=4,
            hotel_nights=7
        )
        
        # Mock API to return emission factors
        with patch.object(self.calculator.api_client, 'get_emission_factor_with_fallback') as mock_factor:
            mock_factor.return_value = 25.0  # Hotel emission factor
            
            result = self.calculator.calculate_total_emissions(trip_data, 0.0)
            
            # Transport emissions should be empty
            assert result.transport_emissions == {}
            
            # Accommodation emissions should be calculated
            expected_accommodation = 7 * 25.0 * 4  # 700 kg CO2e
            assert result.accommodation_emissions == expected_accommodation
            
            # Total should equal accommodation only
            assert result.total_co2e_kg == expected_accommodation
            
            # Per-person should be total divided by travelers
            assert result.per_person_emissions == expected_accommodation / 4
    
    def test_single_traveler_single_night(self):
        """Test minimum viable trip: single traveler, single night"""
        trip_data = TripData(
            origin_city="Bangalore",
            destination_city="Mysore",
            outbound_date=date.today(),
            return_date=date.today() + timedelta(days=1),
            travel_modes=['Bus'],
            num_travelers=1,
            hotel_nights=1
        )
        
        distance_km = 150.0
        
        # Mock API to return emission factors
        with patch.object(self.calculator.api_client, 'get_emission_factor_with_fallback') as mock_factor:
            mock_factor.return_value = 0.05  # Low emission factor
            
            result = self.calculator.calculate_total_emissions(trip_data, distance_km)
            
            # Should calculate correctly for minimum case
            expected_transport = 150.0 * 0.05 * 1  # 7.5 kg CO2e
            expected_accommodation = 1 * 0.05 * 1  # 0.05 kg CO2e
            
            assert result.transport_emissions['Bus'] == expected_transport
            assert result.accommodation_emissions == expected_accommodation
            assert result.per_person_emissions == result.total_co2e_kg  # Same for 1 person
    
    def test_zero_hotel_nights_edge_case(self):
        """Test trip with zero hotel nights (day trip)"""
        trip_data = TripData(
            origin_city="Delhi",
            destination_city="Agra",
            outbound_date=date.today(),
            return_date=date.today(),  # Same day return
            travel_modes=['Car', 'Train'],
            num_travelers=3,
            hotel_nights=0  # Day trip
        )
        
        distance_km = 200.0
        
        # Mock API to return emission factors
        with patch.object(self.calculator.api_client, 'get_emission_factor_with_fallback') as mock_factor:
            mock_factor.return_value = 0.15
            
            result = self.calculator.calculate_total_emissions(trip_data, distance_km)
            
            # Accommodation emissions should be zero
            assert result.accommodation_emissions == 0.0
            
            # Transport emissions should be calculated normally
            expected_transport_per_mode = 200.0 * 0.15 * 3  # 90 kg CO2e per mode
            
            # Check that both modes are present and have correct values
            assert 'Car' in result.transport_emissions, f"Car not found in {result.transport_emissions}"
            assert 'Train' in result.transport_emissions, f"Train not found in {result.transport_emissions}"
            assert result.transport_emissions['Car'] == expected_transport_per_mode
            assert result.transport_emissions['Train'] == expected_transport_per_mode
            
            # Total should equal transport only
            expected_total = expected_transport_per_mode * 2  # Two modes
            assert result.total_co2e_kg == expected_total
    
    def test_very_long_distance_trip(self):
        """Test emissions calculation for very long distance trips"""
        trip_data = TripData(
            origin_city="Kashmir",
            destination_city="Kanyakumari",
            outbound_date=date.today(),
            return_date=date.today() + timedelta(days=14),
            travel_modes=['Flight'],
            num_travelers=2,
            hotel_nights=14
        )
        
        # Very long distance (across India)
        distance_km = 3500.0
        
        # Mock API to return emission factors
        with patch.object(self.calculator.api_client, 'get_emission_factor_with_fallback') as mock_factor:
            mock_factor.return_value = 0.3  # Higher emission factor for flights
            
            result = self.calculator.calculate_total_emissions(trip_data, distance_km)
            
            # Should handle large numbers correctly
            expected_transport = 3500.0 * 0.3 * 2  # 2,100 kg CO2e
            expected_accommodation = 14 * 0.3 * 2  # 8.4 kg CO2e
            
            assert result.transport_emissions['Flight'] == expected_transport
            assert result.accommodation_emissions == expected_accommodation
            
            # Total should be sum of components
            expected_total = expected_transport + expected_accommodation
            assert result.total_co2e_kg == expected_total
    
    def test_all_transport_modes_combination(self):
        """Test emissions calculation with all available transport modes"""
        trip_data = TripData(
            origin_city="Kolkata",
            destination_city="Pune",
            outbound_date=date.today(),
            return_date=date.today() + timedelta(days=5),
            travel_modes=['Flight', 'Train', 'Car', 'Bus'],  # All modes
            num_travelers=2,
            hotel_nights=5
        )
        
        distance_km = 1200.0
        
        # Mock API to return different emission factors for each mode
        def mock_emission_factor(mode, distance=None):
            factors = {
                'Flight': 0.25,
                'Train': 0.04,
                'Car': 0.17,
                'Bus': 0.09,
                'Hotel': 30.0
            }
            return factors.get(mode, 0.0)
        
        with patch.object(self.calculator.api_client, 'get_emission_factor_with_fallback', side_effect=mock_emission_factor):
            result = self.calculator.calculate_total_emissions(trip_data, distance_km)
            
            # Each mode should have different emissions based on its factor
            assert result.transport_emissions['Flight'] == 600.0  # 1200.0 * 0.25 * 2
            assert result.transport_emissions['Train'] == 96.0    # 1200.0 * 0.04 * 2
            assert result.transport_emissions['Car'] == 408.0     # 1200.0 * 0.17 * 2
            assert result.transport_emissions['Bus'] == 216.0     # 1200.0 * 0.09 * 2
            
            # Accommodation should use hotel factor
            assert result.accommodation_emissions == 300.0  # 5 * 30.0 * 2
            
            # Total should be sum of all components
            expected_total = 600.0 + 96.0 + 408.0 + 216.0 + 300.0  # 1,620 kg CO2e
            assert result.total_co2e_kg == expected_total
    
    def test_api_unavailable_fallback_behavior(self):
        """Test behavior when API is completely unavailable"""
        trip_data = TripData(
            origin_city="Jaipur",
            destination_city="Udaipur",
            outbound_date=date.today(),
            return_date=None,
            travel_modes=['Car'],
            num_travelers=2,
            hotel_nights=2
        )
        
        distance_km = 400.0
        
        # Mock API to always return 0.0 (unavailable/no fallback)
        with patch.object(self.calculator.api_client, 'get_emission_factor_with_fallback') as mock_factor:
            mock_factor.return_value = 0.0  # API unavailable, no fallback
            
            result = self.calculator.calculate_total_emissions(trip_data, distance_km)
            
            # Should handle gracefully with zero emissions
            # When emission factor is 0, the mode won't be added to transport_emissions dict
            assert result.transport_emissions == {}  # Empty dict when no valid emissions
            assert result.accommodation_emissions == 0.0
            assert result.total_co2e_kg == 0.0
            assert result.per_person_emissions == 0.0
    
    def test_invalid_input_validation(self):
        """Test input validation for edge cases"""
        # Valid trip data
        valid_trip_data = TripData(
            origin_city="Chennai",
            destination_city="Bangalore",
            outbound_date=date.today(),
            return_date=None,
            travel_modes=['Train'],
            num_travelers=1,
            hotel_nights=0
        )
        
        # Test with negative distance
        assert self.calculator.validate_calculation_inputs(valid_trip_data, -100.0) == False
        
        # Test with zero distance
        assert self.calculator.validate_calculation_inputs(valid_trip_data, 0.0) == False
        
        # Test with valid distance
        assert self.calculator.validate_calculation_inputs(valid_trip_data, 100.0) == True
        
        # Test with invalid trip data (no travel modes)
        invalid_trip_data = TripData(
            origin_city="",  # Empty city
            destination_city="Bangalore",
            outbound_date=date.today(),
            return_date=None,
            travel_modes=[],  # No travel modes
            num_travelers=0,  # Zero travelers
            hotel_nights=-1   # Negative nights
        )
        
        assert self.calculator.validate_calculation_inputs(invalid_trip_data, 100.0) == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])