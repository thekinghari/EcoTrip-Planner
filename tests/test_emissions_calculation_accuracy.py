"""
Property-based tests for emissions calculation accuracy

Feature: ecotrip-planner, Property 3: Emissions Calculation Accuracy
Validates: Requirements 2.4, 2.5, 4.2
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from datetime import date, timedelta
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the path so we can import components
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.models import TripData
from components.carbon_calculator import CarbonCalculator


# Hypothesis strategies for generating test data
@st.composite
def valid_trip_data_strategy(draw):
    """Generate valid TripData instances for calculation testing"""
    origin_city = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=3, max_size=20))
    destination_city = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=3, max_size=20))
    
    # Ensure cities are different
    if origin_city == destination_city:
        destination_city = destination_city + "X"
    
    outbound_date = draw(st.dates(
        min_value=date.today(),
        max_value=date.today() + timedelta(days=365)
    ))
    
    return_date = draw(st.one_of(
        st.none(),
        st.dates(
            min_value=outbound_date + timedelta(days=1),
            max_value=outbound_date + timedelta(days=30)
        )
    ))
    
    travel_modes = draw(st.lists(
        st.sampled_from(['Flight', 'Train', 'Car', 'Bus']),
        min_size=1,
        max_size=4,
        unique=True
    ))
    
    num_travelers = draw(st.integers(min_value=1, max_value=20))
    hotel_nights = draw(st.integers(min_value=0, max_value=30))
    
    return TripData(
        origin_city=origin_city,
        destination_city=destination_city,
        outbound_date=outbound_date,
        return_date=return_date,
        travel_modes=travel_modes,
        num_travelers=num_travelers,
        hotel_nights=hotel_nights
    )


class TestEmissionsCalculationAccuracy:
    """Property-based tests for emissions calculation accuracy"""
    
    def setup_method(self):
        """Set up test environment"""
        self.calculator = CarbonCalculator()
    
    @given(valid_trip_data_strategy(), st.floats(min_value=1.0, max_value=5000.0))
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_total_emissions_equals_sum_of_components(self, trip_data, distance_km):
        """
        Property 3: Emissions Calculation Accuracy - Component Sum Consistency
        For any valid trip data, total emissions should equal sum of transport and accommodation
        """
        # Mock API to return consistent emission factors
        with patch.object(self.calculator.api_client, 'get_emission_factor_with_fallback') as mock_factor:
            mock_factor.return_value = 0.1  # Fixed factor for consistency
            
            result = self.calculator.calculate_total_emissions(trip_data, distance_km)
            
            # Total should equal sum of transport and accommodation
            transport_total = sum(result.transport_emissions.values())
            calculated_total = transport_total + result.accommodation_emissions
            
            # Allow for small floating point differences
            assert abs(result.total_co2e_kg - calculated_total) < 0.001
    
    @given(valid_trip_data_strategy(), st.floats(min_value=1.0, max_value=5000.0))
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_emissions_scale_linearly_with_travelers(self, trip_data, distance_km):
        """
        Property 3: Emissions Calculation Accuracy - Linear Scaling
        For any valid trip data, emissions should scale linearly with number of travelers
        """
        # Mock API to return consistent emission factors
        with patch.object(self.calculator.api_client, 'get_emission_factor_with_fallback') as mock_factor:
            mock_factor.return_value = 0.1  # Fixed factor for consistency
            
            # Calculate emissions for original number of travelers
            result1 = self.calculator.calculate_total_emissions(trip_data, distance_km)
            
            # Create trip data with double the travelers
            trip_data_double = TripData(
                origin_city=trip_data.origin_city,
                destination_city=trip_data.destination_city,
                outbound_date=trip_data.outbound_date,
                return_date=trip_data.return_date,
                travel_modes=trip_data.travel_modes,
                num_travelers=trip_data.num_travelers * 2,
                hotel_nights=trip_data.hotel_nights
            )
            
            result2 = self.calculator.calculate_total_emissions(trip_data_double, distance_km)
            
            # Emissions should double when travelers double
            expected_total = result1.total_co2e_kg * 2
            
            # Allow for small floating point differences
            assert abs(result2.total_co2e_kg - expected_total) < 0.01
    
    @given(valid_trip_data_strategy(), st.floats(min_value=1.0, max_value=5000.0))
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_per_person_emissions_consistency(self, trip_data, distance_km):
        """
        Property 3: Emissions Calculation Accuracy - Per Person Calculation
        For any valid trip data, per-person emissions should be total divided by travelers
        """
        # Mock API to return consistent emission factors
        with patch.object(self.calculator.api_client, 'get_emission_factor_with_fallback') as mock_factor:
            mock_factor.return_value = 0.1  # Fixed factor for consistency
            
            result = self.calculator.calculate_total_emissions(trip_data, distance_km)
            
            # Per-person should be total divided by number of travelers
            expected_per_person = result.total_co2e_kg / trip_data.num_travelers
            
            # Allow for small floating point differences
            assert abs(result.per_person_emissions - expected_per_person) < 0.001
    
    @given(st.sampled_from(['Flight', 'Train', 'Car', 'Bus']), 
           st.floats(min_value=1.0, max_value=5000.0),
           st.integers(min_value=1, max_value=20))
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_transport_emissions_calculation_formula(self, mode, distance_km, num_travelers):
        """
        Property 3: Emissions Calculation Accuracy - Transport Formula
        For any transport mode, emissions should follow: distance * factor * travelers
        """
        # Mock API to return known emission factor
        emission_factor = 0.15
        with patch.object(self.calculator.api_client, 'get_emission_factor_with_fallback') as mock_factor:
            mock_factor.return_value = emission_factor
            
            result = self.calculator.calculate_emissions_by_mode(mode, distance_km, num_travelers)
            
            # Should follow the formula: distance * factor * travelers
            expected_emissions = distance_km * emission_factor * num_travelers
            
            # Allow for small floating point differences
            assert abs(result - expected_emissions) < 0.001
    
    @given(st.integers(min_value=0, max_value=30), st.integers(min_value=1, max_value=20))
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_accommodation_emissions_calculation_formula(self, hotel_nights, num_travelers):
        """
        Property 3: Emissions Calculation Accuracy - Accommodation Formula
        For any accommodation data, emissions should follow: nights * factor * travelers
        """
        # Mock API to return known emission factor
        emission_factor = 25.0
        with patch.object(self.calculator.api_client, 'get_emission_factor_with_fallback') as mock_factor:
            mock_factor.return_value = emission_factor
            
            result = self.calculator.calculate_accommodation_emissions_per_night(num_travelers)
            
            # Should follow the formula: factor * travelers (per night)
            expected_emissions = emission_factor * num_travelers
            
            # Allow for small floating point differences
            assert abs(result - expected_emissions) < 0.001
    
    @given(valid_trip_data_strategy(), st.floats(min_value=1.0, max_value=5000.0))
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_zero_hotel_nights_produces_zero_accommodation_emissions(self, trip_data, distance_km):
        """
        Property 3: Emissions Calculation Accuracy - Zero Accommodation
        For any trip with zero hotel nights, accommodation emissions should be zero
        """
        # Set hotel nights to zero
        trip_data_no_hotel = TripData(
            origin_city=trip_data.origin_city,
            destination_city=trip_data.destination_city,
            outbound_date=trip_data.outbound_date,
            return_date=trip_data.return_date,
            travel_modes=trip_data.travel_modes,
            num_travelers=trip_data.num_travelers,
            hotel_nights=0
        )
        
        # Mock API to return consistent emission factors
        with patch.object(self.calculator.api_client, 'get_emission_factor_with_fallback') as mock_factor:
            mock_factor.return_value = 0.1  # Fixed factor for consistency
            
            result = self.calculator.calculate_total_emissions(trip_data_no_hotel, distance_km)
            
            # Accommodation emissions should be zero
            assert result.accommodation_emissions == 0.0
    
    @given(valid_trip_data_strategy(), st.floats(min_value=1.0, max_value=5000.0))
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_emissions_are_non_negative(self, trip_data, distance_km):
        """
        Property 3: Emissions Calculation Accuracy - Non-negative Results
        For any valid trip data, all emission values should be non-negative
        """
        # Mock API to return positive emission factors
        with patch.object(self.calculator.api_client, 'get_emission_factor_with_fallback') as mock_factor:
            mock_factor.return_value = 0.1  # Positive factor
            
            result = self.calculator.calculate_total_emissions(trip_data, distance_km)
            
            # All emissions should be non-negative
            assert result.total_co2e_kg >= 0.0
            assert result.accommodation_emissions >= 0.0
            assert result.per_person_emissions >= 0.0
            
            for mode_emissions in result.transport_emissions.values():
                assert mode_emissions >= 0.0
    
    @given(valid_trip_data_strategy(), st.floats(min_value=1.0, max_value=5000.0))
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_calculation_with_zero_emission_factor(self, trip_data, distance_km):
        """
        Property 3: Emissions Calculation Accuracy - Zero Factor Handling
        For any trip data with zero emission factors, emissions should be zero
        """
        # Mock API to return zero emission factors
        with patch.object(self.calculator.api_client, 'get_emission_factor_with_fallback') as mock_factor:
            mock_factor.return_value = 0.0  # Zero factor
            
            result = self.calculator.calculate_total_emissions(trip_data, distance_km)
            
            # All emissions should be zero when factors are zero
            assert result.total_co2e_kg == 0.0
            assert result.accommodation_emissions == 0.0
            assert result.per_person_emissions == 0.0
            
            for mode_emissions in result.transport_emissions.values():
                assert mode_emissions == 0.0
    
    @given(valid_trip_data_strategy())
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_calculation_input_validation(self, trip_data):
        """
        Property 3: Emissions Calculation Accuracy - Input Validation
        For any trip data, validation should correctly identify valid/invalid inputs
        """
        # Valid distance should pass validation
        valid_distance = 100.0
        assert self.calculator.validate_calculation_inputs(trip_data, valid_distance) == True
        
        # Zero or negative distance should fail validation
        invalid_distances = [0.0, -1.0, -100.0]
        for invalid_distance in invalid_distances:
            assert self.calculator.validate_calculation_inputs(trip_data, invalid_distance) == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])