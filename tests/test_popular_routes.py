"""
Property-based tests for popular route auto-population

Feature: ecotrip-planner, Property 8: Popular Route Auto-Population
Validates: Requirements 1.7
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
import sys
import os

# Add the project root to the path so we can import components
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.ui_components import FormComponents


class TestPopularRouteAutoPopulation:
    """Property-based tests for popular route auto-population functionality"""
    
    @given(
        route_key=st.sampled_from(list(FormComponents.POPULAR_ROUTES.keys()))
    )
    def test_popular_route_auto_population_correctness(self, route_key):
        """
        Property 8: Popular Route Auto-Population
        For any selection from the popular routes dropdown, the system should 
        correctly auto-populate the origin and destination fields with the 
        corresponding city pair from the predefined list
        """
        # Get the expected origin and destination for this route
        expected_origin, expected_destination = FormComponents.POPULAR_ROUTES[route_key]
        
        # Use the auto-population function
        populated_data = FormComponents.populate_popular_routes(route_key)
        
        # Verify the populated data matches the expected values
        assert populated_data['origin_city'] == expected_origin
        assert populated_data['destination_city'] == expected_destination
    
    def test_invalid_route_key_returns_empty(self):
        """
        Property 8: Popular Route Auto-Population - Invalid Key Handling
        For any invalid route key (not in the predefined list), 
        the auto-population should return empty data
        """
        # Test with various invalid keys
        invalid_keys = [
            "NonExistentRoute",
            "",
            "Invalid to Invalid",
            "Random Route Name",
            None
        ]
        
        for invalid_key in invalid_keys:
            populated_data = FormComponents.populate_popular_routes(invalid_key)
            
            # Should return empty dict for invalid keys
            assert populated_data == {}
    
    @given(
        route_key=st.sampled_from(list(FormComponents.POPULAR_ROUTES.keys()))
    )
    def test_popular_routes_have_different_cities(self, route_key):
        """
        Property 8: Popular Route Auto-Population - City Uniqueness
        For any popular route, the origin and destination cities should be different
        """
        origin, destination = FormComponents.POPULAR_ROUTES[route_key]
        
        # Origin and destination should never be the same
        assert origin != destination
        assert origin.lower() != destination.lower()
    
    @given(
        route_key=st.sampled_from(list(FormComponents.POPULAR_ROUTES.keys()))
    )
    def test_popular_routes_have_valid_city_names(self, route_key):
        """
        Property 8: Popular Route Auto-Population - Valid City Names
        For any popular route, both origin and destination should be non-empty strings
        """
        origin, destination = FormComponents.POPULAR_ROUTES[route_key]
        
        # Both cities should be non-empty strings
        assert isinstance(origin, str)
        assert isinstance(destination, str)
        assert len(origin.strip()) > 0
        assert len(destination.strip()) > 0
    
    def test_all_popular_routes_are_accessible(self):
        """
        Property 8: Popular Route Auto-Population - Complete Coverage
        All routes in POPULAR_ROUTES should be accessible through auto-population
        """
        # Test that every route in the dictionary can be auto-populated
        for route_key in FormComponents.POPULAR_ROUTES.keys():
            populated_data = FormComponents.populate_popular_routes(route_key)
            
            # Should return valid data for every predefined route
            assert 'origin_city' in populated_data
            assert 'destination_city' in populated_data
            assert populated_data['origin_city'] != ""
            assert populated_data['destination_city'] != ""
    
    def test_popular_routes_consistency(self):
        """
        Property 8: Popular Route Auto-Population - Data Consistency
        The POPULAR_ROUTES dictionary should maintain consistent structure
        """
        # Verify the structure of POPULAR_ROUTES
        assert isinstance(FormComponents.POPULAR_ROUTES, dict)
        assert len(FormComponents.POPULAR_ROUTES) > 0
        
        # Each entry should be a tuple of two strings
        for route_name, (origin, destination) in FormComponents.POPULAR_ROUTES.items():
            assert isinstance(route_name, str)
            assert isinstance(origin, str)
            assert isinstance(destination, str)
            assert len(route_name.strip()) > 0
            assert len(origin.strip()) > 0
            assert len(destination.strip()) > 0
    
    @given(
        route_key=st.sampled_from(list(FormComponents.POPULAR_ROUTES.keys()))
    )
    def test_auto_population_idempotency(self, route_key):
        """
        Property 8: Popular Route Auto-Population - Idempotency
        For any route key, calling auto-population multiple times should 
        return the same result
        """
        # Call auto-population multiple times
        result1 = FormComponents.populate_popular_routes(route_key)
        result2 = FormComponents.populate_popular_routes(route_key)
        result3 = FormComponents.populate_popular_routes(route_key)
        
        # All results should be identical
        assert result1 == result2 == result3
    
    def test_popular_routes_include_indian_cities(self):
        """
        Property 8: Popular Route Auto-Population - Indian Context
        Popular routes should include well-known Indian cities
        """
        # Extract all cities from popular routes
        all_cities = set()
        for origin, destination in FormComponents.POPULAR_ROUTES.values():
            all_cities.add(origin)
            all_cities.add(destination)
        
        # Should include some major Indian cities
        expected_indian_cities = {'Salem', 'Chennai', 'Delhi', 'Mumbai', 'Bangalore'}
        
        # At least some of these cities should be present
        intersection = all_cities.intersection(expected_indian_cities)
        assert len(intersection) > 0, f"Expected some Indian cities, but found: {all_cities}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])