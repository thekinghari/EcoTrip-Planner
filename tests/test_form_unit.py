"""
Unit tests for form rendering and validation

Tests specific examples and edge cases for form functionality.
Requirements: 1.1, 1.2, 1.3, 1.4
"""

import pytest
from datetime import date, timedelta
import sys
import os

# Add the project root to the path so we can import components
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.ui_components import FormComponents


class TestFormValidationUnits:
    """Unit tests for specific form validation scenarios"""
    
    def test_valid_complete_form_data(self):
        """Test validation of a complete, valid form submission"""
        form_data = {
            'origin_city': 'Salem',
            'destination_city': 'Chennai',
            'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
            'return_date': (date.today() + timedelta(days=3)).isoformat(),
            'travel_modes': ['Flight', 'Train'],
            'num_travelers': 2,
            'hotel_nights': 2
        }
        
        result = FormComponents.validate_form_data(form_data)
        
        assert result['is_valid'] == True
        assert len(result['errors']) == 0
    
    def test_minimal_valid_form_data(self):
        """Test validation of minimal valid form (one-way trip, no hotel)"""
        form_data = {
            'origin_city': 'Delhi',
            'destination_city': 'Mumbai',
            'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
            'return_date': None,
            'travel_modes': ['Bus'],
            'num_travelers': 1,
            'hotel_nights': 0
        }
        
        result = FormComponents.validate_form_data(form_data)
        
        assert result['is_valid'] == True
        assert len(result['errors']) == 0
    
    def test_empty_origin_city(self):
        """Test validation fails for empty origin city"""
        form_data = {
            'origin_city': '',
            'destination_city': 'Chennai',
            'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
            'return_date': None,
            'travel_modes': ['Flight'],
            'num_travelers': 1,
            'hotel_nights': 0
        }
        
        result = FormComponents.validate_form_data(form_data)
        
        assert result['is_valid'] == False
        assert 'Origin city is required' in result['errors']
    
    def test_empty_destination_city(self):
        """Test validation fails for empty destination city"""
        form_data = {
            'origin_city': 'Salem',
            'destination_city': '',
            'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
            'return_date': None,
            'travel_modes': ['Flight'],
            'num_travelers': 1,
            'hotel_nights': 0
        }
        
        result = FormComponents.validate_form_data(form_data)
        
        assert result['is_valid'] == False
        assert 'Destination city is required' in result['errors']
    
    def test_whitespace_only_cities(self):
        """Test validation handles whitespace-only city names"""
        form_data = {
            'origin_city': '   ',
            'destination_city': '\t\n',
            'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
            'return_date': None,
            'travel_modes': ['Flight'],
            'num_travelers': 1,
            'hotel_nights': 0
        }
        
        result = FormComponents.validate_form_data(form_data)
        
        assert result['is_valid'] == False
        # Should fail because whitespace-only strings are effectively empty
        assert 'Origin city is required' in result['errors']
        assert 'Destination city is required' in result['errors']
    
    def test_missing_outbound_date(self):
        """Test validation fails for missing outbound date"""
        form_data = {
            'origin_city': 'Salem',
            'destination_city': 'Chennai',
            'outbound_date': None,
            'return_date': None,
            'travel_modes': ['Flight'],
            'num_travelers': 1,
            'hotel_nights': 0
        }
        
        result = FormComponents.validate_form_data(form_data)
        
        assert result['is_valid'] == False
        assert 'Outbound date is required' in result['errors']
    
    def test_boundary_travelers_values(self):
        """Test boundary values for number of travelers"""
        # Test minimum valid value
        form_data_min = {
            'origin_city': 'Salem',
            'destination_city': 'Chennai',
            'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
            'return_date': None,
            'travel_modes': ['Flight'],
            'num_travelers': 1,
            'hotel_nights': 0
        }
        
        result_min = FormComponents.validate_form_data(form_data_min)
        assert result_min['is_valid'] == True
        
        # Test maximum valid value
        form_data_max = {
            'origin_city': 'Salem',
            'destination_city': 'Chennai',
            'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
            'return_date': None,
            'travel_modes': ['Flight'],
            'num_travelers': 20,
            'hotel_nights': 0
        }
        
        result_max = FormComponents.validate_form_data(form_data_max)
        assert result_max['is_valid'] == True
    
    def test_boundary_hotel_nights_values(self):
        """Test boundary values for hotel nights"""
        # Test minimum valid value
        form_data_min = {
            'origin_city': 'Salem',
            'destination_city': 'Chennai',
            'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
            'return_date': None,
            'travel_modes': ['Flight'],
            'num_travelers': 1,
            'hotel_nights': 0
        }
        
        result_min = FormComponents.validate_form_data(form_data_min)
        assert result_min['is_valid'] == True
        
        # Test maximum valid value
        form_data_max = {
            'origin_city': 'Salem',
            'destination_city': 'Chennai',
            'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
            'return_date': None,
            'travel_modes': ['Flight'],
            'num_travelers': 1,
            'hotel_nights': 365
        }
        
        result_max = FormComponents.validate_form_data(form_data_max)
        assert result_max['is_valid'] == True
    
    def test_all_travel_modes_valid(self):
        """Test that all individual travel modes are valid"""
        valid_modes = ['Flight', 'Train', 'Car', 'Bus']
        
        for mode in valid_modes:
            form_data = {
                'origin_city': 'Salem',
                'destination_city': 'Chennai',
                'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
                'return_date': None,
                'travel_modes': [mode],
                'num_travelers': 1,
                'hotel_nights': 0
            }
            
            result = FormComponents.validate_form_data(form_data)
            assert result['is_valid'] == True, f"Mode {mode} should be valid"
    
    def test_multiple_travel_modes_valid(self):
        """Test that multiple travel modes can be selected"""
        form_data = {
            'origin_city': 'Salem',
            'destination_city': 'Chennai',
            'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
            'return_date': None,
            'travel_modes': ['Flight', 'Train', 'Car', 'Bus'],
            'num_travelers': 1,
            'hotel_nights': 0
        }
        
        result = FormComponents.validate_form_data(form_data)
        assert result['is_valid'] == True
    
    def test_case_insensitive_same_cities(self):
        """Test that same cities with different cases are rejected"""
        test_cases = [
            ('salem', 'Salem'),
            ('CHENNAI', 'chennai'),
            ('Delhi', 'DELHI'),
            ('mumbai', 'Mumbai')
        ]
        
        for origin, destination in test_cases:
            form_data = {
                'origin_city': origin,
                'destination_city': destination,
                'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
                'return_date': None,
                'travel_modes': ['Flight'],
                'num_travelers': 1,
                'hotel_nights': 0
            }
            
            result = FormComponents.validate_form_data(form_data)
            assert result['is_valid'] == False
            assert 'Origin and destination cities cannot be the same' in result['errors']
    
    def test_return_date_same_as_outbound(self):
        """Test that return date same as outbound date is rejected"""
        same_date = (date.today() + timedelta(days=1)).isoformat()
        
        form_data = {
            'origin_city': 'Salem',
            'destination_city': 'Chennai',
            'outbound_date': same_date,
            'return_date': same_date,
            'travel_modes': ['Flight'],
            'num_travelers': 1,
            'hotel_nights': 0
        }
        
        result = FormComponents.validate_form_data(form_data)
        assert result['is_valid'] == False
        assert 'Return date must be after outbound date' in result['errors']
    
    def test_invalid_date_format(self):
        """Test handling of invalid date formats"""
        form_data = {
            'origin_city': 'Salem',
            'destination_city': 'Chennai',
            'outbound_date': 'invalid-date',
            'return_date': None,
            'travel_modes': ['Flight'],
            'num_travelers': 1,
            'hotel_nights': 0
        }
        
        result = FormComponents.validate_form_data(form_data)
        assert result['is_valid'] == False
        assert 'Invalid date format' in result['errors']
    
    def test_multiple_validation_errors(self):
        """Test that multiple validation errors are captured"""
        form_data = {
            'origin_city': '',  # Missing origin
            'destination_city': '',  # Missing destination
            'outbound_date': (date.today() - timedelta(days=1)).isoformat(),  # Past date
            'return_date': None,
            'travel_modes': [],  # No travel modes
            'num_travelers': 0,  # Invalid travelers
            'hotel_nights': -1  # Invalid hotel nights
        }
        
        result = FormComponents.validate_form_data(form_data)
        assert result['is_valid'] == False
        
        # Should have multiple errors
        assert len(result['errors']) >= 5
        assert any('Origin city is required' in error for error in result['errors'])
        assert any('Destination city is required' in error for error in result['errors'])
        assert any('Outbound date cannot be in the past' in error for error in result['errors'])
        assert any('At least one travel mode must be selected' in error for error in result['errors'])
        assert any('travelers must be at least 1' in error for error in result['errors'])
        assert any('Hotel nights cannot be negative' in error for error in result['errors'])


class TestPopularRoutesUnits:
    """Unit tests for popular routes functionality"""
    
    def test_popular_routes_structure(self):
        """Test that POPULAR_ROUTES has expected structure"""
        routes = FormComponents.POPULAR_ROUTES
        
        assert isinstance(routes, dict)
        assert len(routes) > 0
        
        # Check a few specific routes exist
        assert "Salem to Chennai" in routes
        assert "Delhi to Mumbai" in routes
        
        # Verify structure of entries
        salem_chennai = routes["Salem to Chennai"]
        assert salem_chennai == ("Salem", "Chennai")
    
    def test_populate_specific_routes(self):
        """Test auto-population of specific known routes"""
        # Test Salem to Chennai
        result = FormComponents.populate_popular_routes("Salem to Chennai")
        assert result == {'origin_city': 'Salem', 'destination_city': 'Chennai'}
        
        # Test Delhi to Mumbai
        result = FormComponents.populate_popular_routes("Delhi to Mumbai")
        assert result == {'origin_city': 'Delhi', 'destination_city': 'Mumbai'}
    
    def test_populate_nonexistent_route(self):
        """Test auto-population with non-existent route"""
        result = FormComponents.populate_popular_routes("Nonexistent Route")
        assert result == {}
    
    def test_populate_none_route(self):
        """Test auto-population with None input"""
        result = FormComponents.populate_popular_routes(None)
        assert result == {}
    
    def test_travel_modes_list(self):
        """Test that TRAVEL_MODES contains expected modes"""
        modes = FormComponents.TRAVEL_MODES
        
        assert isinstance(modes, list)
        assert len(modes) == 4
        assert "Flight" in modes
        assert "Train" in modes
        assert "Car" in modes
        assert "Bus" in modes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])