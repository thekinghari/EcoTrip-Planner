"""
Property-based tests for input validation

Feature: ecotrip-planner, Property 1: Input Validation Consistency
Validates: Requirements 1.5, 1.6
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from datetime import date, timedelta
import sys
import os

# Add the project root to the path so we can import components
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.ui_components import FormComponents


class TestInputValidation:
    """Property-based tests for form input validation"""
    
    @given(
        num_travelers=st.integers(min_value=1, max_value=20),
        hotel_nights=st.integers(min_value=0, max_value=365)
    )
    def test_valid_numeric_inputs_accepted(self, num_travelers, hotel_nights):
        """
        Property 1: Input Validation Consistency - Valid Numeric Inputs
        For any valid numeric input (travelers 1-20, hotel nights 0-365), 
        the validation should accept the values
        """
        # Create form data with valid numeric inputs
        form_data = {
            'origin_city': 'Salem',
            'destination_city': 'Chennai',
            'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
            'return_date': None,
            'travel_modes': ['Flight'],
            'num_travelers': num_travelers,
            'hotel_nights': hotel_nights
        }
        
        # Validate the form data
        validation_result = FormComponents.validate_form_data(form_data)
        
        # Should be valid since all inputs are within acceptable ranges
        assert validation_result['is_valid'] == True
        assert len(validation_result['errors']) == 0
    
    @given(
        num_travelers=st.integers(max_value=0),  # Invalid: <= 0
    )
    def test_invalid_travelers_rejected(self, num_travelers):
        """
        Property 1: Input Validation Consistency - Invalid Travelers
        For any invalid number of travelers (negative or zero), 
        the validation should reject the input
        """
        # Create form data with invalid number of travelers
        form_data = {
            'origin_city': 'Salem',
            'destination_city': 'Chennai',
            'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
            'return_date': None,
            'travel_modes': ['Flight'],
            'num_travelers': num_travelers,
            'hotel_nights': 1
        }
        
        # Validate the form data
        validation_result = FormComponents.validate_form_data(form_data)
        
        # Should be invalid due to invalid number of travelers
        assert validation_result['is_valid'] == False
        assert any('travelers must be at least 1' in error for error in validation_result['errors'])
    
    @given(
        num_travelers=st.integers(min_value=21, max_value=100),  # Invalid: > 20
    )
    def test_excessive_travelers_rejected(self, num_travelers):
        """
        Property 1: Input Validation Consistency - Excessive Travelers
        For any excessive number of travelers (> 20), 
        the validation should reject the input
        """
        # Create form data with excessive number of travelers
        form_data = {
            'origin_city': 'Salem',
            'destination_city': 'Chennai',
            'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
            'return_date': None,
            'travel_modes': ['Flight'],
            'num_travelers': num_travelers,
            'hotel_nights': 1
        }
        
        # Validate the form data
        validation_result = FormComponents.validate_form_data(form_data)
        
        # Should be invalid due to excessive number of travelers
        assert validation_result['is_valid'] == False
        assert any('travelers cannot exceed 20' in error for error in validation_result['errors'])
    
    @given(
        hotel_nights=st.integers(max_value=-1),  # Invalid: < 0
    )
    def test_negative_hotel_nights_rejected(self, hotel_nights):
        """
        Property 1: Input Validation Consistency - Negative Hotel Nights
        For any negative number of hotel nights, 
        the validation should reject the input
        """
        # Create form data with negative hotel nights
        form_data = {
            'origin_city': 'Salem',
            'destination_city': 'Chennai',
            'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
            'return_date': None,
            'travel_modes': ['Flight'],
            'num_travelers': 2,
            'hotel_nights': hotel_nights
        }
        
        # Validate the form data
        validation_result = FormComponents.validate_form_data(form_data)
        
        # Should be invalid due to negative hotel nights
        assert validation_result['is_valid'] == False
        assert any('Hotel nights cannot be negative' in error for error in validation_result['errors'])
    
    @given(
        hotel_nights=st.integers(min_value=366, max_value=1000),  # Invalid: > 365
    )
    def test_excessive_hotel_nights_rejected(self, hotel_nights):
        """
        Property 1: Input Validation Consistency - Excessive Hotel Nights
        For any excessive number of hotel nights (> 365), 
        the validation should reject the input
        """
        # Create form data with excessive hotel nights
        form_data = {
            'origin_city': 'Salem',
            'destination_city': 'Chennai',
            'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
            'return_date': None,
            'travel_modes': ['Flight'],
            'num_travelers': 2,
            'hotel_nights': hotel_nights
        }
        
        # Validate the form data
        validation_result = FormComponents.validate_form_data(form_data)
        
        # Should be invalid due to excessive hotel nights
        assert validation_result['is_valid'] == False
        assert any('Hotel nights cannot exceed 365' in error for error in validation_result['errors'])
    
    @given(
        origin_city=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=2, max_size=20)
    )
    def test_same_origin_destination_rejected(self, origin_city):
        """
        Property 1: Input Validation Consistency - Same Origin and Destination
        For any case where origin and destination cities are the same (case-insensitive), 
        the validation should reject the input
        """
        # Make destination same as origin (case-insensitive)
        same_destination = origin_city.lower()
        same_origin = origin_city.lower()
        
        # Create form data with same origin and destination
        form_data = {
            'origin_city': same_origin,
            'destination_city': same_destination,
            'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
            'return_date': None,
            'travel_modes': ['Flight'],
            'num_travelers': 2,
            'hotel_nights': 1
        }
        
        # Validate the form data
        validation_result = FormComponents.validate_form_data(form_data)
        
        # Should be invalid due to same origin and destination
        assert validation_result['is_valid'] == False
        assert any('Origin and destination cities cannot be the same' in error for error in validation_result['errors'])
    
    @given(
        travel_modes=st.lists(
            st.sampled_from(['InvalidMode1', 'InvalidMode2', 'NotAMode']),
            min_size=1,
            max_size=3
        )
    )
    def test_invalid_travel_modes_rejected(self, travel_modes):
        """
        Property 1: Input Validation Consistency - Invalid Travel Modes
        For any invalid travel modes (not in the allowed list), 
        the validation should reject the input
        """
        # Create form data with invalid travel modes
        form_data = {
            'origin_city': 'Salem',
            'destination_city': 'Chennai',
            'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
            'return_date': None,
            'travel_modes': travel_modes,
            'num_travelers': 2,
            'hotel_nights': 1
        }
        
        # Validate the form data
        validation_result = FormComponents.validate_form_data(form_data)
        
        # Should be invalid due to invalid travel modes
        assert validation_result['is_valid'] == False
        assert any('Invalid travel mode selected' in error for error in validation_result['errors'])
    
    @given(
        travel_modes=st.lists(
            st.sampled_from(['Flight', 'Train', 'Car', 'Bus']),
            min_size=1,
            max_size=4,
            unique=True
        )
    )
    def test_valid_travel_modes_accepted(self, travel_modes):
        """
        Property 1: Input Validation Consistency - Valid Travel Modes
        For any valid combination of travel modes from the allowed list, 
        the validation should accept the input
        """
        # Create form data with valid travel modes
        form_data = {
            'origin_city': 'Salem',
            'destination_city': 'Chennai',
            'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
            'return_date': None,
            'travel_modes': travel_modes,
            'num_travelers': 2,
            'hotel_nights': 1
        }
        
        # Validate the form data
        validation_result = FormComponents.validate_form_data(form_data)
        
        # Should be valid since travel modes are from allowed list
        assert validation_result['is_valid'] == True
        assert len(validation_result['errors']) == 0
    
    def test_empty_travel_modes_rejected(self):
        """
        Property 1: Input Validation Consistency - Empty Travel Modes
        For empty travel modes list, the validation should reject the input
        """
        # Create form data with empty travel modes
        form_data = {
            'origin_city': 'Salem',
            'destination_city': 'Chennai',
            'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
            'return_date': None,
            'travel_modes': [],
            'num_travelers': 2,
            'hotel_nights': 1
        }
        
        # Validate the form data
        validation_result = FormComponents.validate_form_data(form_data)
        
        # Should be invalid due to empty travel modes
        assert validation_result['is_valid'] == False
        assert any('At least one travel mode must be selected' in error for error in validation_result['errors'])
    
    @given(
        days_in_past=st.integers(min_value=1, max_value=365)
    )
    def test_past_outbound_date_rejected(self, days_in_past):
        """
        Property 1: Input Validation Consistency - Past Outbound Date
        For any outbound date in the past, the validation should reject the input
        """
        # Create form data with past outbound date
        past_date = date.today() - timedelta(days=days_in_past)
        form_data = {
            'origin_city': 'Salem',
            'destination_city': 'Chennai',
            'outbound_date': past_date.isoformat(),
            'return_date': None,
            'travel_modes': ['Flight'],
            'num_travelers': 2,
            'hotel_nights': 1
        }
        
        # Validate the form data
        validation_result = FormComponents.validate_form_data(form_data)
        
        # Should be invalid due to past outbound date
        assert validation_result['is_valid'] == False
        assert any('Outbound date cannot be in the past' in error for error in validation_result['errors'])
    
    @given(
        days_offset=st.integers(min_value=1, max_value=30)
    )
    def test_return_before_outbound_rejected(self, days_offset):
        """
        Property 1: Input Validation Consistency - Return Before Outbound
        For any return date that is before or same as outbound date, 
        the validation should reject the input
        """
        # Create dates where return is before outbound
        outbound_date = date.today() + timedelta(days=10)
        return_date = outbound_date - timedelta(days=days_offset)
        
        form_data = {
            'origin_city': 'Salem',
            'destination_city': 'Chennai',
            'outbound_date': outbound_date.isoformat(),
            'return_date': return_date.isoformat(),
            'travel_modes': ['Flight'],
            'num_travelers': 2,
            'hotel_nights': 1
        }
        
        # Validate the form data
        validation_result = FormComponents.validate_form_data(form_data)
        
        # Should be invalid due to return date before outbound date
        assert validation_result['is_valid'] == False
        assert any('Return date must be after outbound date' in error for error in validation_result['errors'])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])