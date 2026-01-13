"""
Property-based tests for geographic distance calculations

Feature: ecotrip-planner, Property 5: Geographic Distance Calculation
Validates: Requirements 2.3, 8.1, 8.3

Feature: ecotrip-planner, Property 12: Dual Input Method Support
Validates: Requirements 8.4
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
import sys
import os
import math

# Add the project root to the path so we can import components
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.geographic_data import GeographicDataManager
from components.models import GeographicLocation


class TestGeographicDistanceCalculation:
    """Property-based tests for geographic distance calculations"""
    
    def setup_method(self):
        """Set up geographic data manager for each test"""
        self.geo_manager = GeographicDataManager()
    
    @given(st.sampled_from(['Salem', 'Chennai', 'Delhi', 'Mumbai', 'Bangalore', 'Kolkata', 'Hyderabad', 'Pune']))
    def test_distance_calculation_consistency(self, city_name):
        """
        Property 5: Geographic Distance Calculation - Consistency
        For any valid Indian city, distance calculations should be consistent and accurate
        """
        # Distance from a city to itself should be 0
        distance_to_self = self.geo_manager.calculate_geodesic_distance(city_name, city_name)
        assert distance_to_self is not None
        assert distance_to_self == 0.0
    
    @given(
        st.sampled_from(['Salem', 'Chennai', 'Delhi', 'Mumbai', 'Bangalore', 'Kolkata']),
        st.sampled_from(['Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Kochi', 'Goa'])
    )
    def test_distance_symmetry(self, city1, city2):
        """
        Property 5: Geographic Distance Calculation - Symmetry
        For any pair of cities, distance from A to B should equal distance from B to A
        """
        distance_ab = self.geo_manager.calculate_geodesic_distance(city1, city2)
        distance_ba = self.geo_manager.calculate_geodesic_distance(city2, city1)
        
        assert distance_ab is not None
        assert distance_ba is not None
        
        # Should be equal (allowing for floating point precision)
        assert abs(distance_ab - distance_ba) < 0.001
    
    @given(
        st.sampled_from(['Salem', 'Chennai', 'Delhi', 'Mumbai']),
        st.sampled_from(['Bangalore', 'Kolkata', 'Hyderabad', 'Pune']),
        st.sampled_from(['Ahmedabad', 'Jaipur', 'Kochi', 'Goa'])
    )
    def test_triangle_inequality(self, city1, city2, city3):
        """
        Property 5: Geographic Distance Calculation - Triangle Inequality
        For any three cities, the direct distance should be less than or equal to the sum of indirect distances
        """
        # Skip if any cities are the same
        if city1 == city2 or city2 == city3 or city1 == city3:
            return
        
        distance_12 = self.geo_manager.calculate_geodesic_distance(city1, city2)
        distance_23 = self.geo_manager.calculate_geodesic_distance(city2, city3)
        distance_13 = self.geo_manager.calculate_geodesic_distance(city1, city3)
        
        assert distance_12 is not None
        assert distance_23 is not None
        assert distance_13 is not None
        
        # Triangle inequality: direct distance <= sum of two sides
        assert distance_13 <= distance_12 + distance_23 + 0.001  # Small tolerance for floating point
    
    @given(st.sampled_from(['Salem', 'Chennai', 'Delhi', 'Mumbai', 'Bangalore', 'Kolkata', 'Hyderabad', 'Pune']))
    def test_coordinate_retrieval_accuracy(self, city_name):
        """
        Property 5: Geographic Distance Calculation - Coordinate Accuracy
        For any valid city, coordinates should be retrievable and within valid ranges
        """
        coordinates = self.geo_manager.get_city_coordinates(city_name)
        
        assert coordinates is not None
        latitude, longitude = coordinates
        
        # Latitude should be between -90 and 90
        assert -90 <= latitude <= 90
        
        # Longitude should be between -180 and 180
        assert -180 <= longitude <= 180
        
        # For Indian cities, latitude should be roughly between 6 and 37 degrees North
        assert 6 <= latitude <= 37
        
        # For Indian cities, longitude should be roughly between 68 and 97 degrees East
        assert 68 <= longitude <= 97
    
    def test_known_distance_accuracy(self):
        """
        Property 5: Geographic Distance Calculation - Known Distance Accuracy
        For known city pairs, calculated distances should be reasonably accurate
        """
        # Test some well-known distances (approximate values based on actual geodesic calculations)
        known_distances = {
            ('Salem', 'Chennai'): (275, 285),  # ~279 km
            ('Delhi', 'Mumbai'): (1145, 1155),  # ~1150 km
            ('Bangalore', 'Chennai'): (285, 295),  # ~291 km
        }
        
        for (city1, city2), (min_dist, max_dist) in known_distances.items():
            calculated_distance = self.geo_manager.calculate_geodesic_distance(city1, city2)
            assert calculated_distance is not None
            assert min_dist <= calculated_distance <= max_dist, f"Distance between {city1} and {city2} should be between {min_dist} and {max_dist}, got {calculated_distance}"
    
    @given(st.text(min_size=1, max_size=20))
    def test_invalid_city_handling(self, invalid_city):
        """
        Property 5: Geographic Distance Calculation - Invalid City Handling
        For any invalid city name, the system should handle gracefully
        """
        # Skip if the random text happens to be a valid city
        if invalid_city in self.geo_manager.get_all_cities():
            return
        
        coordinates = self.geo_manager.get_city_coordinates(invalid_city)
        assert coordinates is None
        
        # Distance calculation with invalid city should return None
        valid_city = 'Chennai'
        distance = self.geo_manager.calculate_geodesic_distance(invalid_city, valid_city)
        assert distance is None
        
        distance_reverse = self.geo_manager.calculate_geodesic_distance(valid_city, invalid_city)
        assert distance_reverse is None
    
    @given(st.sampled_from(['Salem', 'Chennai', 'Delhi', 'Mumbai', 'Bangalore']))
    def test_city_validation_consistency(self, city_name):
        """
        Property 5: Geographic Distance Calculation - City Validation Consistency
        For any valid city, validation should be consistent with coordinate availability
        """
        is_valid = self.geo_manager.validate_city_names(city_name)
        coordinates = self.geo_manager.get_city_coordinates(city_name)
        
        # If city is valid, coordinates should be available
        if is_valid:
            assert coordinates is not None
        
        # If coordinates are available, city should be valid
        if coordinates is not None:
            assert is_valid
    
    @given(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=10))
    def test_city_suggestions_relevance(self, partial_name):
        """
        Property 5: Geographic Distance Calculation - City Suggestions Relevance
        For any partial city name, suggestions should contain the partial name as substring
        """
        suggestions = self.geo_manager.get_city_suggestions(partial_name)
        
        # All suggestions should contain the partial name (case insensitive)
        for suggestion in suggestions:
            assert partial_name.lower() in suggestion.lower()
        
        # Should return at most 5 suggestions
        assert len(suggestions) <= 5
    
    def test_all_cities_have_coordinates(self):
        """
        Property 5: Geographic Distance Calculation - Complete City Data
        All cities in the database should have valid coordinates
        """
        all_cities = self.geo_manager.get_all_cities()
        
        for city in all_cities:
            coordinates = self.geo_manager.get_city_coordinates(city)
            assert coordinates is not None, f"City {city} should have coordinates"
            
            latitude, longitude = coordinates
            assert isinstance(latitude, (int, float))
            assert isinstance(longitude, (int, float))
            assert not math.isnan(latitude)
            assert not math.isnan(longitude)


class TestDualInputMethodSupport:
    """Property-based tests for dual input method support"""
    
    def setup_method(self):
        """Set up geographic data manager for each test"""
        self.geo_manager = GeographicDataManager()
    
    @given(st.sampled_from(['Salem', 'Chennai', 'Delhi', 'Mumbai', 'Bangalore', 'Kolkata', 'Hyderabad', 'Pune']))
    def test_predefined_city_selection_consistency(self, city_name):
        """
        Property 12: Dual Input Method Support - Predefined Selection Consistency
        For any city in the predefined list, both selection and manual input should produce valid results
        """
        # Test predefined city selection (via get_city_coordinates)
        coordinates_predefined = self.geo_manager.get_city_coordinates(city_name)
        assert coordinates_predefined is not None
        
        # Test manual input validation (via validate_city_names)
        is_valid_manual = self.geo_manager.validate_city_names(city_name)
        assert is_valid_manual == True
        
        # Both methods should be consistent
        city_info = self.geo_manager.get_city_info(city_name)
        assert city_info is not None
        assert city_info.city_name == city_name
    
    @given(st.sampled_from(['Salem', 'Chennai', 'Delhi', 'Mumbai', 'Bangalore']))
    def test_city_list_completeness(self, city_name):
        """
        Property 12: Dual Input Method Support - City List Completeness
        For any valid city, it should appear in the complete city list
        """
        all_cities = self.geo_manager.get_all_cities()
        
        # City should be in the complete list
        assert city_name in all_cities
        
        # City should be valid
        assert self.geo_manager.validate_city_names(city_name)
        
        # City should have coordinates
        coordinates = self.geo_manager.get_city_coordinates(city_name)
        assert coordinates is not None
    
    @given(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=2, max_size=8))
    def test_manual_input_suggestion_system(self, partial_input):
        """
        Property 12: Dual Input Method Support - Manual Input Suggestion System
        For any partial manual input, the suggestion system should provide relevant options
        """
        suggestions = self.geo_manager.get_city_suggestions(partial_input)
        
        # All suggestions should be valid cities
        for suggestion in suggestions:
            assert self.geo_manager.validate_city_names(suggestion)
            assert self.geo_manager.get_city_coordinates(suggestion) is not None
        
        # Suggestions should contain the partial input (case insensitive)
        for suggestion in suggestions:
            assert partial_input.lower() in suggestion.lower()
        
        # Should not exceed maximum suggestion count
        assert len(suggestions) <= 5
    
    def test_popular_routes_dual_support(self):
        """
        Property 12: Dual Input Method Support - Popular Routes Dual Support
        Popular routes should support both predefined selection and manual validation
        """
        popular_routes = self.geo_manager.get_popular_routes()
        
        for origin, destination in popular_routes:
            # Both cities should be valid via predefined selection
            assert self.geo_manager.validate_city_names(origin)
            assert self.geo_manager.validate_city_names(destination)
            
            # Both cities should have coordinates
            origin_coords = self.geo_manager.get_city_coordinates(origin)
            dest_coords = self.geo_manager.get_city_coordinates(destination)
            assert origin_coords is not None
            assert dest_coords is not None
            
            # Distance calculation should work
            distance = self.geo_manager.calculate_geodesic_distance(origin, destination)
            assert distance is not None
            assert distance > 0  # Cities should be different
    
    @given(
        st.sampled_from(['Salem', 'Chennai', 'Delhi', 'Mumbai']),
        st.sampled_from(['Bangalore', 'Kolkata', 'Hyderabad', 'Pune'])
    )
    def test_input_method_equivalence(self, city1, city2):
        """
        Property 12: Dual Input Method Support - Input Method Equivalence
        For any pair of cities, results should be equivalent regardless of input method
        """
        # Method 1: Direct city name validation and coordinate retrieval
        is_valid1 = self.geo_manager.validate_city_names(city1)
        is_valid2 = self.geo_manager.validate_city_names(city2)
        coords1 = self.geo_manager.get_city_coordinates(city1)
        coords2 = self.geo_manager.get_city_coordinates(city2)
        
        # Method 2: Via city info retrieval
        info1 = self.geo_manager.get_city_info(city1)
        info2 = self.geo_manager.get_city_info(city2)
        
        # Both methods should be consistent
        if is_valid1 and is_valid2:
            assert coords1 is not None
            assert coords2 is not None
            assert info1 is not None
            assert info2 is not None
            
            # Coordinates should match
            assert coords1 == (info1.latitude, info1.longitude)
            assert coords2 == (info2.latitude, info2.longitude)
            
            # Distance calculation should be consistent
            distance_direct = self.geo_manager.calculate_geodesic_distance(city1, city2)
            distance_via_info = info1.calculate_distance_to(info2)
            
            assert distance_direct is not None
            assert abs(distance_direct - distance_via_info) < 0.001  # Should be essentially equal
    
    def test_input_validation_consistency(self):
        """
        Property 12: Dual Input Method Support - Input Validation Consistency
        Input validation should be consistent across all input methods
        """
        all_cities = self.geo_manager.get_all_cities()
        
        for city in all_cities:
            # All cities in the list should be valid
            assert self.geo_manager.validate_city_names(city)
            
            # All cities should have coordinates
            coordinates = self.geo_manager.get_city_coordinates(city)
            assert coordinates is not None
            
            # All cities should have complete info
            city_info = self.geo_manager.get_city_info(city)
            assert city_info is not None
            assert city_info.city_name == city
        
        # Invalid cities should consistently return None/False
        invalid_city = "NonExistentCity123"
        assert not self.geo_manager.validate_city_names(invalid_city)
        assert self.geo_manager.get_city_coordinates(invalid_city) is None
        assert self.geo_manager.get_city_info(invalid_city) is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])