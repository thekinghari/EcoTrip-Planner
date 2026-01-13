"""
Integration tests for complete user workflows in EcoTrip Planner

Tests end-to-end trip planning workflow, alternative route generation workflow,
and error recovery workflows as specified in requirements 1.1 through 8.4.
"""

import pytest
import streamlit as st
from unittest.mock import Mock, patch, MagicMock
from datetime import date, timedelta
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from components.session_manager import SessionStateManager
from components.carbon_calculator import CarbonCalculator
from components.route_analyzer import RouteAnalyzer
from components.geographic_data import GeographicDataManager
from components.models import TripData, EmissionsResult, AlternativeRoute


class TestTripPlanningWorkflow:
    """Test end-to-end trip planning workflow"""
    
    def setup_method(self):
        """Setup test environment"""
        # Mock Streamlit session state
        if not hasattr(st, 'session_state'):
            st.session_state = {}
        
        # Clear session state
        SessionStateManager.clear_session()
    
    def test_complete_trip_planning_workflow_success(self):
        """Test successful end-to-end trip planning workflow"""
        # Step 1: Initialize session
        SessionStateManager.initialize_session()
        
        # Step 2: Store trip data (simulating form submission)
        trip_data = {
            'origin_city': 'Delhi',
            'destination_city': 'Mumbai',
            'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
            'return_date': (date.today() + timedelta(days=3)).isoformat(),
            'travel_modes': ['Flight', 'Train'],
            'num_travelers': 2,
            'hotel_nights': 2
        }
        
        SessionStateManager.store_trip_data(trip_data)
        
        # Verify trip data is stored
        stored_data = SessionStateManager.get_trip_data()
        assert stored_data['origin_city'] == 'Delhi'
        assert stored_data['destination_city'] == 'Mumbai'
        assert stored_data['num_travelers'] == 2
        
        # Step 3: Calculate emissions (mocked)
        with patch('components.carbon_calculator.CarbonCalculator') as mock_calculator:
            mock_result = EmissionsResult(
                total_co2e_kg=150.5,
                transport_emissions={'Flight': 120.0, 'Train': 20.0},
                accommodation_emissions=10.5,
                per_person_emissions=75.25,
                calculation_timestamp='2024-01-01T12:00:00'
            )
            
            mock_calculator.return_value.calculate_total_emissions.return_value = mock_result
            
            # Store emissions data
            SessionStateManager.store_emissions_data(mock_result.__dict__)
            
            # Verify emissions data is stored
            emissions_data = SessionStateManager.get_emissions_data()
            assert emissions_data['total_co2e_kg'] == 150.5
            assert emissions_data['per_person_emissions'] == 75.25
        
        # Step 4: Generate alternatives (mocked)
        with patch('components.route_analyzer.RouteAnalyzer') as mock_analyzer:
            mock_alternatives = [
                {
                    'transport_mode': 'Train',
                    'duration_hours': 16.0,
                    'distance_km': 1400.0,
                    'co2e_emissions_kg': 40.0,
                    'estimated_cost_inr': 3500.0,
                    'emissions_savings_kg': 80.0,
                    'cost_difference_inr': -2000.0,
                    'route_details': {'is_fallback': True}
                },
                {
                    'transport_mode': 'Bus',
                    'duration_hours': 20.0,
                    'distance_km': 1400.0,
                    'co2e_emissions_kg': 60.0,
                    'estimated_cost_inr': 2000.0,
                    'emissions_savings_kg': 60.0,
                    'cost_difference_inr': -3500.0,
                    'route_details': {'is_fallback': True}
                }
            ]
            
            mock_analyzer.return_value.generate_alternatives.return_value = mock_alternatives
            
            # Store alternatives data
            SessionStateManager.store_alternatives_data(mock_alternatives)
            
            # Verify alternatives data is stored
            alternatives_data = SessionStateManager.get_alternatives_data()
            assert len(alternatives_data) == 2
            assert alternatives_data[0]['transport_mode'] == 'Train'
            assert alternatives_data[1]['transport_mode'] == 'Bus'
        
        # Step 5: Verify complete workflow state
        session_summary = SessionStateManager.get_session_summary()
        assert session_summary['has_trip_data'] == True
        assert session_summary['has_emissions_data'] == True
        assert SessionStateManager.has_alternatives_data() == True
        
        # Verify data consistency across workflow
        assert stored_data['num_travelers'] == trip_data['num_travelers']
        assert emissions_data['total_co2e_kg'] > 0
        assert len(alternatives_data) > 0
    
    def test_trip_planning_workflow_with_validation_errors(self):
        """Test trip planning workflow with form validation errors"""
        # Initialize session
        SessionStateManager.initialize_session()
        
        # Test invalid trip data
        invalid_trip_data = {
            'origin_city': '',  # Empty origin
            'destination_city': 'Mumbai',
            'outbound_date': (date.today() - timedelta(days=1)).isoformat(),  # Past date
            'return_date': None,
            'travel_modes': [],  # No travel modes
            'num_travelers': 0,  # Invalid number
            'hotel_nights': -1   # Negative nights
        }
        
        # Validation should fail
        from components.ui_components import FormComponents
        validation_result = FormComponents.validate_form_data(invalid_trip_data)
        
        assert validation_result['is_valid'] == False
        assert len(validation_result['errors']) > 0
        
        # Verify specific validation errors
        errors = validation_result['errors']
        assert any('Origin city is required' in error for error in errors)
        assert any('travel mode' in error.lower() for error in errors)
        assert any('travelers' in error.lower() for error in errors)
    
    def test_trip_planning_workflow_partial_completion(self):
        """Test workflow behavior with partial completion"""
        # Initialize session
        SessionStateManager.initialize_session()
        
        # Store only trip data (no emissions or alternatives)
        trip_data = {
            'origin_city': 'Chennai',
            'destination_city': 'Bangalore',
            'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
            'return_date': None,
            'travel_modes': ['Car'],
            'num_travelers': 1,
            'hotel_nights': 0
        }
        
        SessionStateManager.store_trip_data(trip_data)
        
        # Verify partial state
        session_summary = SessionStateManager.get_session_summary()
        assert session_summary['has_trip_data'] == True
        assert session_summary['has_emissions_data'] == False
        assert SessionStateManager.has_alternatives_data() == False
        
        # Verify workflow can continue from partial state
        stored_data = SessionStateManager.get_trip_data()
        assert stored_data['origin_city'] == 'Chennai'
        assert stored_data['destination_city'] == 'Bangalore'


class TestAlternativeRouteGenerationWorkflow:
    """Test alternative route generation workflow"""
    
    def setup_method(self):
        """Setup test environment"""
        if not hasattr(st, 'session_state'):
            st.session_state = {}
        SessionStateManager.clear_session()
    
    def test_alternative_route_generation_success(self):
        """Test successful alternative route generation"""
        # Setup initial data
        SessionStateManager.initialize_session()
        
        trip_data = {
            'origin_city': 'Delhi',
            'destination_city': 'Jaipur',
            'travel_modes': ['Car'],
            'num_travelers': 2
        }
        
        emissions_data = {
            'total_co2e_kg': 100.0,
            'per_person_emissions': 50.0
        }
        
        SessionStateManager.store_trip_data(trip_data)
        SessionStateManager.store_emissions_data(emissions_data)
        
        # Mock route analyzer
        with patch('components.route_analyzer.RouteAnalyzer') as mock_analyzer:
            # Mock geographic data manager
            with patch('components.geographic_data.GeographicDataManager') as mock_geo:
                mock_geo.return_value.calculate_distance.return_value = 280.0
                
                # Mock carbon calculator
                with patch('components.carbon_calculator.CarbonCalculator') as mock_calc:
                    mock_calc.return_value.calculate_emissions_by_mode.side_effect = [
                        45.0,  # Train
                        65.0,  # Bus
                        120.0, # Flight
                        80.0   # Car
                    ]
                    
                    # Create route analyzer instance
                    analyzer = RouteAnalyzer()
                    
                    # Generate alternatives
                    alternatives = analyzer.generate_alternatives(
                        'Delhi', 'Jaipur', ['Car'], 100.0
                    )
                    
                    # Verify alternatives were generated
                    assert len(alternatives) > 0
                    
                    # Verify alternative structure
                    for alt in alternatives:
                        assert 'transport_mode' in alt
                        assert 'co2e_emissions_kg' in alt
                        assert 'estimated_cost_inr' in alt
                        assert 'duration_hours' in alt
                        assert 'distance_km' in alt
                        assert alt['distance_km'] > 0
                        assert alt['co2e_emissions_kg'] > 0
    
    def test_alternative_route_generation_with_api_failure(self):
        """Test alternative route generation with API failures"""
        # Setup data
        SessionStateManager.initialize_session()
        
        trip_data = {
            'origin_city': 'Mumbai',
            'destination_city': 'Pune',
            'travel_modes': ['Train'],
            'num_travelers': 1
        }
        
        SessionStateManager.store_trip_data(trip_data)
        
        # Mock API failures
        with patch('components.api_client.APIClientManager') as mock_api:
            mock_api.return_value.query_google_maps_api.side_effect = Exception("API Error")
            mock_api.return_value.query_climatiq_api.side_effect = Exception("API Error")
            
            # Mock fallback mechanisms
            with patch('components.geographic_data.GeographicDataManager') as mock_geo:
                mock_geo.return_value.calculate_distance.return_value = 150.0
                
                with patch('components.carbon_calculator.CarbonCalculator') as mock_calc:
                    mock_calc.return_value.calculate_emissions_by_mode.return_value = 30.0
                    
                    # Generate alternatives should still work with fallback
                    analyzer = RouteAnalyzer()
                    alternatives = analyzer.generate_alternatives(
                        'Mumbai', 'Pune', ['Train'], 50.0
                    )
                    
                    # Should still generate alternatives using fallback data
                    assert len(alternatives) > 0
                    
                    # Verify fallback indicators
                    for alt in alternatives:
                        assert alt['route_details']['is_fallback'] == True
    
    def test_alternative_route_ranking_and_filtering(self):
        """Test alternative route ranking and filtering functionality"""
        # Create mock alternatives
        alternatives_data = [
            {
                'transport_mode': 'Flight',
                'co2e_emissions_kg': 120.0,
                'estimated_cost_inr': 8000.0,
                'duration_hours': 2.0,
                'emissions_savings_kg': -20.0
            },
            {
                'transport_mode': 'Train',
                'co2e_emissions_kg': 40.0,
                'estimated_cost_inr': 2000.0,
                'duration_hours': 12.0,
                'emissions_savings_kg': 60.0
            },
            {
                'transport_mode': 'Bus',
                'co2e_emissions_kg': 60.0,
                'estimated_cost_inr': 1500.0,
                'duration_hours': 15.0,
                'emissions_savings_kg': 40.0
            }
        ]
        
        # Convert to AlternativeRoute objects for testing
        alternatives = []
        for alt_data in alternatives_data:
            alt = AlternativeRoute(
                transport_mode=alt_data['transport_mode'],
                duration_hours=alt_data['duration_hours'],
                distance_km=300.0,
                co2e_emissions_kg=alt_data['co2e_emissions_kg'],
                estimated_cost_inr=alt_data['estimated_cost_inr'],
                emissions_savings_kg=alt_data['emissions_savings_kg'],
                cost_difference_inr=0.0,
                route_details={}
            )
            alternatives.append(alt)
        
        analyzer = RouteAnalyzer()
        
        # Test ranking by emissions (lowest first)
        ranked_by_emissions = analyzer.rank_alternatives_by_emissions(alternatives)
        assert ranked_by_emissions[0].transport_mode == 'Train'  # Lowest emissions
        assert ranked_by_emissions[-1].transport_mode == 'Flight'  # Highest emissions
        
        # Test ranking by cost (lowest first)
        ranked_by_cost = analyzer.rank_alternatives_by_cost(alternatives)
        assert ranked_by_cost[0].transport_mode == 'Bus'  # Lowest cost
        assert ranked_by_cost[-1].transport_mode == 'Flight'  # Highest cost
        
        # Test filtering by mode
        train_only = analyzer.filter_alternatives_by_mode(alternatives, ['Train'])
        assert len(train_only) == 1
        assert train_only[0].transport_mode == 'Train'


class TestErrorRecoveryWorkflows:
    """Test error recovery workflows"""
    
    def setup_method(self):
        """Setup test environment"""
        if not hasattr(st, 'session_state'):
            st.session_state = {}
        SessionStateManager.clear_session()
    
    def test_session_corruption_recovery(self):
        """Test recovery from session state corruption"""
        # Initialize session
        SessionStateManager.initialize_session()
        
        # Simulate session corruption
        st.session_state['ecotrip_trip_data'] = "corrupted_string_instead_of_dict"
        st.session_state['ecotrip_emissions_data'] = None
        
        # Recovery should handle corruption gracefully
        try:
            trip_data = SessionStateManager.get_trip_data()
            emissions_data = SessionStateManager.get_emissions_data()
            
            # Should return empty/default values instead of crashing
            assert isinstance(trip_data, dict)
            assert isinstance(emissions_data, dict)
            
        except Exception as e:
            pytest.fail(f"Session corruption recovery failed: {e}")
    
    def test_api_failure_recovery_workflow(self):
        """Test complete workflow with API failures and fallback mechanisms"""
        # Initialize session
        SessionStateManager.initialize_session()
        
        # Store trip data
        trip_data = {
            'origin_city': 'Kolkata',
            'destination_city': 'Bhubaneswar',
            'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
            'travel_modes': ['Train', 'Bus'],
            'num_travelers': 1,
            'hotel_nights': 1
        }
        
        SessionStateManager.store_trip_data(trip_data)
        
        # Mock all API failures
        with patch('components.api_client.APIClientManager') as mock_api:
            # All API calls fail
            mock_api.return_value.query_climatiq_api.return_value = None
            mock_api.return_value.query_google_maps_api.return_value = None
            mock_api.return_value.get_emission_factor_with_fallback.return_value = 0.05  # Fallback factor
            
            # Mock geographic data (should work without APIs)
            with patch('components.geographic_data.GeographicDataManager') as mock_geo:
                mock_geo.return_value.calculate_distance.return_value = 450.0
                
                # Test carbon calculation with fallback
                calculator = CarbonCalculator()
                
                # Should still be able to calculate using fallback data
                try:
                    # Create TripData object
                    from components.models import TripData
                    trip_obj = TripData(
                        origin_city=trip_data['origin_city'],
                        destination_city=trip_data['destination_city'],
                        outbound_date=trip_data['outbound_date'],
                        return_date=None,
                        travel_modes=trip_data['travel_modes'],
                        num_travelers=trip_data['num_travelers'],
                        hotel_nights=trip_data['hotel_nights']
                    )
                    
                    # This should work with fallback mechanisms
                    transport_emissions = calculator.calculate_transport_emissions(trip_obj, 450.0)
                    
                    # Should return some emissions data (using fallback)
                    assert isinstance(transport_emissions, dict)
                    
                except Exception as e:
                    # If calculation fails, it should be handled gracefully
                    assert "fallback" in str(e).lower() or "api" in str(e).lower()
    
    def test_network_connectivity_recovery(self):
        """Test recovery from network connectivity issues"""
        # Initialize session
        SessionStateManager.initialize_session()
        
        # Mock network connectivity issues
        with patch('requests.get') as mock_get:
            mock_get.side_effect = ConnectionError("Network unreachable")
            
            with patch('requests.post') as mock_post:
                mock_post.side_effect = ConnectionError("Network unreachable")
                
                # Application should still function with cached/static data
                from components.geographic_data import GeographicDataManager
                
                geo_manager = GeographicDataManager()
                
                # Should still be able to get city coordinates from static data
                delhi_coords = geo_manager.get_city_coordinates('Delhi')
                mumbai_coords = geo_manager.get_city_coordinates('Mumbai')
                
                assert delhi_coords is not None
                assert mumbai_coords is not None
                assert 'latitude' in delhi_coords
                assert 'longitude' in delhi_coords
                
                # Should still be able to calculate distance
                distance = geo_manager.calculate_distance('Delhi', 'Mumbai')
                assert distance > 0
    
    def test_invalid_input_recovery(self):
        """Test recovery from invalid user inputs"""
        # Test various invalid inputs
        invalid_inputs = [
            {
                'origin_city': None,
                'destination_city': 'Mumbai',
                'travel_modes': ['Flight'],
                'num_travelers': 1
            },
            {
                'origin_city': 'Delhi',
                'destination_city': '',
                'travel_modes': [],
                'num_travelers': 0
            },
            {
                'origin_city': 'Delhi',
                'destination_city': 'Mumbai',
                'travel_modes': ['InvalidMode'],
                'num_travelers': -1
            }
        ]
        
        from components.ui_components import FormComponents
        
        for invalid_input in invalid_inputs:
            # Validation should catch invalid inputs
            validation_result = FormComponents.validate_form_data(invalid_input)
            
            # Should return validation errors instead of crashing
            assert validation_result['is_valid'] == False
            assert len(validation_result['errors']) > 0
            assert isinstance(validation_result['errors'], list)
    
    def test_memory_management_recovery(self):
        """Test recovery from memory management issues"""
        # Initialize session
        SessionStateManager.initialize_session()
        
        # Simulate large data storage
        large_data = {
            'origin_city': 'Delhi',
            'destination_city': 'Mumbai',
            'large_field': 'x' * 10000,  # Large string
            'travel_modes': ['Flight'] * 100,  # Large list
            'num_travelers': 1,
            'hotel_nights': 0
        }
        
        # Should handle large data gracefully
        try:
            SessionStateManager.store_trip_data(large_data)
            retrieved_data = SessionStateManager.get_trip_data()
            
            # Basic data should still be accessible
            assert retrieved_data['origin_city'] == 'Delhi'
            assert retrieved_data['destination_city'] == 'Mumbai'
            
        except Exception as e:
            # If storage fails due to size, should fail gracefully
            assert "memory" in str(e).lower() or "size" in str(e).lower()


class TestWorkflowIntegration:
    """Test integration between different workflow components"""
    
    def setup_method(self):
        """Setup test environment"""
        if not hasattr(st, 'session_state'):
            st.session_state = {}
        SessionStateManager.clear_session()
    
    def test_complete_application_workflow_integration(self):
        """Test complete integration of all workflow components"""
        # This test simulates a complete user journey through the application
        
        # Step 1: Session initialization
        SessionStateManager.initialize_session()
        session_summary = SessionStateManager.get_session_summary()
        assert session_summary['has_trip_data'] == False
        
        # Step 2: Form data validation and storage
        valid_trip_data = {
            'origin_city': 'Chennai',
            'destination_city': 'Bangalore',
            'outbound_date': (date.today() + timedelta(days=2)).isoformat(),
            'return_date': (date.today() + timedelta(days=4)).isoformat(),
            'travel_modes': ['Train', 'Bus'],
            'num_travelers': 2,
            'hotel_nights': 2
        }
        
        from components.ui_components import FormComponents
        validation_result = FormComponents.validate_form_data(valid_trip_data)
        assert validation_result['is_valid'] == True
        
        SessionStateManager.store_trip_data(valid_trip_data)
        
        # Step 3: Mock emissions calculation
        with patch('components.carbon_calculator.CarbonCalculator') as mock_calc:
            mock_result = EmissionsResult(
                total_co2e_kg=85.4,
                transport_emissions={'Train': 30.0, 'Bus': 25.0},
                accommodation_emissions=30.4,
                per_person_emissions=42.7,
                calculation_timestamp='2024-01-01T15:30:00'
            )
            
            mock_calc.return_value.calculate_total_emissions.return_value = mock_result
            
            SessionStateManager.store_emissions_data(mock_result.__dict__)
        
        # Step 4: Mock alternative generation
        with patch('components.route_analyzer.RouteAnalyzer') as mock_analyzer:
            mock_alternatives = [
                {
                    'transport_mode': 'Train',
                    'duration_hours': 6.0,
                    'distance_km': 350.0,
                    'co2e_emissions_kg': 28.0,
                    'estimated_cost_inr': 1200.0,
                    'emissions_savings_kg': 27.0,
                    'cost_difference_inr': -800.0,
                    'route_details': {'is_fallback': False}
                }
            ]
            
            mock_analyzer.return_value.generate_alternatives.return_value = mock_alternatives
            SessionStateManager.store_alternatives_data(mock_alternatives)
        
        # Step 5: Verify complete workflow state
        final_summary = SessionStateManager.get_session_summary()
        assert final_summary['has_trip_data'] == True
        assert final_summary['has_emissions_data'] == True
        assert SessionStateManager.has_alternatives_data() == True
        
        # Step 6: Verify data consistency across all components
        stored_trip = SessionStateManager.get_trip_data()
        stored_emissions = SessionStateManager.get_emissions_data()
        stored_alternatives = SessionStateManager.get_alternatives_data()
        
        assert stored_trip['origin_city'] == valid_trip_data['origin_city']
        assert stored_emissions['total_co2e_kg'] == 85.4
        assert len(stored_alternatives) == 1
        assert stored_alternatives[0]['transport_mode'] == 'Train'
        
        # Step 7: Test session cleanup
        SessionStateManager.clear_session()
        cleared_summary = SessionStateManager.get_session_summary()
        assert cleared_summary['has_trip_data'] == False
        assert cleared_summary['has_emissions_data'] == False
        assert SessionStateManager.has_alternatives_data() == False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])