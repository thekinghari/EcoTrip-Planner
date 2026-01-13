"""
Property-based tests for session state persistence

Feature: ecotrip-planner, Property 2: Session State Persistence
Validates: Requirements 1.8, 2.7, 5.1, 5.2, 5.3
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the path so we can import components
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.models import TripData, EmissionsResult, AlternativeRoute, GeographicLocation
from components.session_manager import SessionStateManager


class MockSessionState:
    """Mock object that behaves like Streamlit's session_state"""
    def __init__(self):
        self._data = {}
    
    def __contains__(self, key):
        return key in self._data
    
    def __getattr__(self, key):
        return self._data.get(key)
    
    def __setattr__(self, key, value):
        if key.startswith('_'):
            super().__setattr__(key, value)
        else:
            self._data[key] = value
    
    def get(self, key, default=None):
        return self._data.get(key, default)


# Hypothesis strategies for generating test data
@st.composite
def trip_data_strategy(draw):
    """Generate valid TripData instances"""
    # Use simpler text generation to avoid slow generation
    origin_city = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=3, max_size=20))
    destination_city = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=3, max_size=20))
    
    # Ensure cities are different
    if origin_city == destination_city:
        destination_city = destination_city + "X"
    
    outbound_date = draw(st.dates(
        min_value=date.today(),
        max_value=date.today() + timedelta(days=365)
    ))
    
    # Return date can be None or after outbound date
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


@st.composite
def emissions_result_strategy(draw):
    """Generate valid EmissionsResult instances"""
    transport_emissions = draw(st.dictionaries(
        st.sampled_from(['Flight', 'Train', 'Car', 'Bus']),
        st.floats(min_value=0.0, max_value=1000.0),
        min_size=1,
        max_size=4
    ))
    
    accommodation_emissions = draw(st.floats(min_value=0.0, max_value=500.0))
    total_co2e_kg = sum(transport_emissions.values()) + accommodation_emissions
    per_person_emissions = draw(st.floats(min_value=0.0, max_value=total_co2e_kg))
    
    # Use a fixed datetime to avoid flaky strategy issues
    calculation_timestamp = datetime(2026, 1, 12, 12, 0, 0)
    
    return EmissionsResult(
        total_co2e_kg=total_co2e_kg,
        transport_emissions=transport_emissions,
        accommodation_emissions=accommodation_emissions,
        per_person_emissions=per_person_emissions,
        calculation_timestamp=calculation_timestamp
    )


@st.composite
def alternative_route_strategy(draw):
    """Generate valid AlternativeRoute instances"""
    transport_mode = draw(st.sampled_from(['Flight', 'Train', 'Car', 'Bus']))
    duration_hours = draw(st.floats(min_value=0.5, max_value=48.0))
    distance_km = draw(st.floats(min_value=1.0, max_value=5000.0))
    co2e_emissions_kg = draw(st.floats(min_value=0.0, max_value=1000.0))
    estimated_cost_inr = draw(st.floats(min_value=100.0, max_value=50000.0))
    emissions_savings_kg = draw(st.floats(min_value=-100.0, max_value=500.0))
    cost_difference_inr = draw(st.floats(min_value=-10000.0, max_value=10000.0))
    route_details = draw(st.dictionaries(st.text(), st.text(), min_size=0, max_size=5))
    
    return AlternativeRoute(
        transport_mode=transport_mode,
        duration_hours=duration_hours,
        distance_km=distance_km,
        co2e_emissions_kg=co2e_emissions_kg,
        estimated_cost_inr=estimated_cost_inr,
        emissions_savings_kg=emissions_savings_kg,
        cost_difference_inr=cost_difference_inr,
        route_details=route_details
    )


class TestSessionStatePersistence:
    """Property-based tests for session state persistence"""
    
    def setup_method(self):
        """Set up mock Streamlit session state for each test"""
        self.mock_session_state = MockSessionState()
        
        # Mock streamlit.session_state
        self.streamlit_patcher = patch('streamlit.session_state', self.mock_session_state)
        self.streamlit_patcher.start()
    
    def teardown_method(self):
        """Clean up after each test"""
        self.streamlit_patcher.stop()
    
    @given(trip_data_strategy())
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_trip_data_persistence(self, trip_data):
        """
        Property 2: Session State Persistence - Trip Data
        For any valid trip data, storing and retrieving should maintain data consistency
        """
        # Initialize session
        SessionStateManager.initialize_session()
        
        # Convert to dict and store
        trip_dict = trip_data.to_dict()
        SessionStateManager.store_trip_data(trip_dict)
        
        # Retrieve and verify
        retrieved_dict = SessionStateManager.get_trip_data()
        
        # Should be able to reconstruct the original object
        reconstructed_trip = TripData.from_dict(retrieved_dict)
        
        # All fields should match
        assert reconstructed_trip.origin_city == trip_data.origin_city
        assert reconstructed_trip.destination_city == trip_data.destination_city
        assert reconstructed_trip.outbound_date == trip_data.outbound_date
        assert reconstructed_trip.return_date == trip_data.return_date
        assert reconstructed_trip.travel_modes == trip_data.travel_modes
        assert reconstructed_trip.num_travelers == trip_data.num_travelers
        assert reconstructed_trip.hotel_nights == trip_data.hotel_nights
    
    @given(emissions_result_strategy())
    def test_emissions_data_persistence(self, emissions_result):
        """
        Property 2: Session State Persistence - Emissions Data
        For any valid emissions result, storing and retrieving should maintain data consistency
        """
        # Initialize session
        SessionStateManager.initialize_session()
        
        # Convert to dict and store
        emissions_dict = emissions_result.to_dict()
        SessionStateManager.store_emissions_data(emissions_dict)
        
        # Retrieve and verify
        retrieved_dict = SessionStateManager.get_emissions_data()
        
        # Should be able to reconstruct the original object
        reconstructed_emissions = EmissionsResult.from_dict(retrieved_dict)
        
        # All fields should match
        assert reconstructed_emissions.total_co2e_kg == emissions_result.total_co2e_kg
        assert reconstructed_emissions.transport_emissions == emissions_result.transport_emissions
        assert reconstructed_emissions.accommodation_emissions == emissions_result.accommodation_emissions
        assert reconstructed_emissions.per_person_emissions == emissions_result.per_person_emissions
        assert reconstructed_emissions.calculation_timestamp == emissions_result.calculation_timestamp
    
    @given(st.lists(alternative_route_strategy(), min_size=0, max_size=10))
    def test_alternatives_data_persistence(self, alternatives_list):
        """
        Property 2: Session State Persistence - Alternatives Data
        For any list of alternative routes, storing and retrieving should maintain data consistency
        """
        # Initialize session
        SessionStateManager.initialize_session()
        
        # Convert to dicts and store
        alternatives_dicts = [alt.to_dict() for alt in alternatives_list]
        SessionStateManager.store_alternatives_data(alternatives_dicts)
        
        # Retrieve and verify
        retrieved_dicts = SessionStateManager.get_alternatives_data()
        
        # Should be able to reconstruct all original objects
        reconstructed_alternatives = [AlternativeRoute.from_dict(alt_dict) for alt_dict in retrieved_dicts]
        
        # Lists should have same length
        assert len(reconstructed_alternatives) == len(alternatives_list)
        
        # All objects should match
        for original, reconstructed in zip(alternatives_list, reconstructed_alternatives):
            assert reconstructed.transport_mode == original.transport_mode
            assert reconstructed.duration_hours == original.duration_hours
            assert reconstructed.distance_km == original.distance_km
            assert reconstructed.co2e_emissions_kg == original.co2e_emissions_kg
            assert reconstructed.estimated_cost_inr == original.estimated_cost_inr
            assert reconstructed.emissions_savings_kg == original.emissions_savings_kg
            assert reconstructed.cost_difference_inr == original.cost_difference_inr
            assert reconstructed.route_details == original.route_details
    
    @given(st.booleans())
    def test_calculation_status_persistence(self, status):
        """
        Property 2: Session State Persistence - Calculation Status
        For any boolean status, storing and retrieving should maintain consistency
        """
        # Initialize session
        SessionStateManager.initialize_session()
        
        # Store status
        SessionStateManager.set_calculation_status(status)
        
        # Retrieve and verify
        retrieved_status = SessionStateManager.is_calculation_in_progress()
        
        assert retrieved_status == status
    
    def test_session_initialization_idempotency(self):
        """
        Property 2: Session State Persistence - Initialization Idempotency
        Multiple initializations should not affect existing data
        """
        # Initialize session
        SessionStateManager.initialize_session()
        
        # Store some test data
        test_data = {'test': 'value'}
        SessionStateManager.store_trip_data(test_data)
        
        # Initialize again
        SessionStateManager.initialize_session()
        
        # Data should still be there
        retrieved_data = SessionStateManager.get_trip_data()
        assert retrieved_data == test_data
    
    def test_session_clear_completeness(self):
        """
        Property 2: Session State Persistence - Clear Completeness
        Clearing session should reset all data to initial state
        """
        # Initialize session
        SessionStateManager.initialize_session()
        
        # Store various types of data
        SessionStateManager.store_trip_data({'test': 'trip'})
        SessionStateManager.store_emissions_data({'test': 'emissions'})
        SessionStateManager.store_alternatives_data([{'test': 'alternative'}])
        SessionStateManager.set_calculation_status(True)
        
        # Clear session
        SessionStateManager.clear_session()
        
        # All data should be reset to defaults
        assert SessionStateManager.get_trip_data() == {}
        assert SessionStateManager.get_emissions_data() == {}
        assert SessionStateManager.get_alternatives_data() == []
        assert SessionStateManager.is_calculation_in_progress() == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])