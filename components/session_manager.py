"""
Session state management for EcoTrip Planner

Handles Streamlit session state operations for maintaining user data
and calculation results throughout the application session.
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from .models import TripData, EmissionsResult, AlternativeRoute


class SessionStateManager:
    """Manages session state for the EcoTrip Planner application"""
    
    # Session state keys
    TRIP_DATA_KEY = 'trip_data'
    EMISSIONS_DATA_KEY = 'emissions_data'
    ALTERNATIVES_DATA_KEY = 'alternatives_data'
    CALCULATION_STATUS_KEY = 'calculation_in_progress'
    
    @staticmethod
    def initialize_session() -> None:
        """Initialize session state with default values"""
        # Only initialize if keys don't exist to preserve existing data
        if SessionStateManager.TRIP_DATA_KEY not in st.session_state:
            setattr(st.session_state, SessionStateManager.TRIP_DATA_KEY, {})
        
        if SessionStateManager.EMISSIONS_DATA_KEY not in st.session_state:
            setattr(st.session_state, SessionStateManager.EMISSIONS_DATA_KEY, {})
        
        if SessionStateManager.ALTERNATIVES_DATA_KEY not in st.session_state:
            setattr(st.session_state, SessionStateManager.ALTERNATIVES_DATA_KEY, [])
        
        if SessionStateManager.CALCULATION_STATUS_KEY not in st.session_state:
            setattr(st.session_state, SessionStateManager.CALCULATION_STATUS_KEY, False)
    
    @staticmethod
    def store_trip_data(trip_data: Dict[str, Any]) -> None:
        """Store trip data in session state with validation"""
        if not isinstance(trip_data, dict):
            raise ValueError("Trip data must be a dictionary")
        
        # Validate that we can reconstruct a TripData object if data is complete
        if trip_data and all(key in trip_data for key in ['origin_city', 'destination_city', 'outbound_date', 'travel_modes', 'num_travelers', 'hotel_nights']):
            try:
                # Validate by attempting to create TripData object
                TripData.from_dict(trip_data)
            except Exception as e:
                raise ValueError(f"Invalid trip data format: {e}")
        
        setattr(st.session_state, SessionStateManager.TRIP_DATA_KEY, trip_data)
    
    @staticmethod
    def get_trip_data() -> Dict[str, Any]:
        """Retrieve trip data from session state"""
        return getattr(st.session_state, SessionStateManager.TRIP_DATA_KEY, {})
    
    @staticmethod
    def store_emissions_data(emissions_data: Dict[str, Any]) -> None:
        """Store emissions calculation results in session state with validation"""
        if not isinstance(emissions_data, dict):
            raise ValueError("Emissions data must be a dictionary")
        
        # Validate that we can reconstruct an EmissionsResult object if data is complete
        if emissions_data and all(key in emissions_data for key in ['total_co2e_kg', 'transport_emissions', 'accommodation_emissions', 'per_person_emissions', 'calculation_timestamp']):
            try:
                # Validate by attempting to create EmissionsResult object
                # This will handle both string and datetime timestamps
                EmissionsResult.from_dict(emissions_data)
            except (ValueError, TypeError, KeyError) as e:
                # If validation fails, log but don't raise - allow storage of partial data
                import logging
                logging.warning(f"Emissions data validation warning: {e}")
                # Still store the data - it might be valid but with different format
        
        setattr(st.session_state, SessionStateManager.EMISSIONS_DATA_KEY, emissions_data)
    
    @staticmethod
    def get_emissions_data() -> Dict[str, Any]:
        """Retrieve emissions data from session state"""
        return getattr(st.session_state, SessionStateManager.EMISSIONS_DATA_KEY, {})
    
    @staticmethod
    def store_alternatives_data(alternatives: List[Dict[str, Any]]) -> None:
        """Store alternative routes data in session state with validation"""
        if not isinstance(alternatives, list):
            raise ValueError("Alternatives data must be a list")
        
        # Validate each alternative route if the list is not empty
        for i, alt_data in enumerate(alternatives):
            if not isinstance(alt_data, dict):
                raise ValueError(f"Alternative route {i} must be a dictionary")
            
            # Validate that we can reconstruct an AlternativeRoute object if data is complete
            if alt_data and all(key in alt_data for key in ['transport_mode', 'duration_hours', 'distance_km', 'co2e_emissions_kg', 'estimated_cost_inr', 'emissions_savings_kg', 'cost_difference_inr', 'route_details']):
                try:
                    # Validate by attempting to create AlternativeRoute object
                    AlternativeRoute.from_dict(alt_data)
                except Exception as e:
                    raise ValueError(f"Invalid alternative route {i} data format: {e}")
        
        setattr(st.session_state, SessionStateManager.ALTERNATIVES_DATA_KEY, alternatives)
    
    @staticmethod
    def get_alternatives_data() -> List[Dict[str, Any]]:
        """Retrieve alternatives data from session state"""
        return getattr(st.session_state, SessionStateManager.ALTERNATIVES_DATA_KEY, [])
    
    @staticmethod
    def clear_session() -> None:
        """Clear all session data and reset to initial state"""
        setattr(st.session_state, SessionStateManager.TRIP_DATA_KEY, {})
        setattr(st.session_state, SessionStateManager.EMISSIONS_DATA_KEY, {})
        setattr(st.session_state, SessionStateManager.ALTERNATIVES_DATA_KEY, [])
        setattr(st.session_state, SessionStateManager.CALCULATION_STATUS_KEY, False)
    
    @staticmethod
    def set_calculation_status(in_progress: bool) -> None:
        """Set calculation progress status with validation"""
        if not isinstance(in_progress, bool):
            raise ValueError("Calculation status must be a boolean")
        
        setattr(st.session_state, SessionStateManager.CALCULATION_STATUS_KEY, in_progress)
    
    @staticmethod
    def is_calculation_in_progress() -> bool:
        """Check if calculation is currently in progress"""
        return getattr(st.session_state, SessionStateManager.CALCULATION_STATUS_KEY, False)
    
    @staticmethod
    def has_trip_data() -> bool:
        """Check if valid trip data exists in session"""
        trip_data = SessionStateManager.get_trip_data()
        return bool(trip_data and 'origin_city' in trip_data and 'destination_city' in trip_data)
    
    @staticmethod
    def has_emissions_data() -> bool:
        """Check if valid emissions data exists in session"""
        emissions_data = SessionStateManager.get_emissions_data()
        return bool(emissions_data and 'total_co2e_kg' in emissions_data)
    
    @staticmethod
    def has_alternatives_data() -> bool:
        """Check if alternatives data exists in session"""
        alternatives_data = SessionStateManager.get_alternatives_data()
        return bool(alternatives_data)
    
    @staticmethod
    def get_session_summary() -> Dict[str, Any]:
        """Get a summary of current session state for debugging"""
        return {
            'has_trip_data': SessionStateManager.has_trip_data(),
            'has_emissions_data': SessionStateManager.has_emissions_data(),
            'has_alternatives_data': SessionStateManager.has_alternatives_data(),
            'calculation_in_progress': SessionStateManager.is_calculation_in_progress(),
            'trip_data_keys': list(SessionStateManager.get_trip_data().keys()),
            'emissions_data_keys': list(SessionStateManager.get_emissions_data().keys()),
            'alternatives_count': len(SessionStateManager.get_alternatives_data())
        }
    
    @staticmethod
    def reset_calculations() -> None:
        """Reset only calculation results while preserving trip input data"""
        setattr(st.session_state, SessionStateManager.EMISSIONS_DATA_KEY, {})
        setattr(st.session_state, SessionStateManager.ALTERNATIVES_DATA_KEY, [])
        setattr(st.session_state, SessionStateManager.CALCULATION_STATUS_KEY, False)