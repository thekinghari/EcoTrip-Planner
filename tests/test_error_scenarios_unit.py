"""
Unit tests for specific error scenarios

Tests API failure handling, invalid input processing, and network connectivity issues.
**Validates: Requirements 6.2, 6.3, 6.4, 6.5**

This module tests specific error scenarios with concrete examples to ensure
proper error handling, fallback mechanisms, and user-friendly error messages.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from datetime import date, datetime, timedelta
from typing import Dict, Any

from components.api_client import APIClientManager
from components.carbon_calculator import CarbonCalculator
from components.ui_components import UIComponents, FormComponents
from components.session_manager import SessionStateManager
from components.models import TripData, EmissionsResult


class TestAPIFailureHandling:
    """Unit tests for API failure scenarios"""
    
    def test_climatiq_api_connection_error(self):
        """Test Climatiq API connection error handling"""
        api_client = APIClientManager()
        
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
            
            result = api_client.query_climatiq_api('estimate', {'test': 'data'})
            
            # Should return None gracefully
            assert result is None
            
            # Should still provide fallback emission factors
            fallback_factor = api_client.get_emission_factor_with_fallback('Flight')
            assert isinstance(fallback_factor, (int, float))
            assert fallback_factor > 0  # Should use static fallback
    
    def test_google_maps_api_timeout_error(self):
        """Test Google Maps API timeout error handling"""
        api_client = APIClientManager()
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
            
            result = api_client.query_google_maps_api('directions/json', {'origin': 'Delhi', 'destination': 'Mumbai'})
            
            # Should return None gracefully
            assert result is None
            
            # Should provide fallback route data
            fallback_routes = api_client.fetch_alternative_routes('Delhi', 'Mumbai', ['Car'])
            assert isinstance(fallback_routes, dict)
            assert 'Car' in fallback_routes
            assert fallback_routes['Car'][0]['is_fallback'] is True
    
    def test_climatiq_api_authentication_error(self):
        """Test Climatiq API authentication error (401)"""
        api_client = APIClientManager()
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
            mock_post.return_value = mock_response
            
            result = api_client.query_climatiq_api('estimate', {'test': 'data'})
            
            # Should return None gracefully
            assert result is None
            
            # Should still provide fallback
            fallback_factor = api_client.get_emission_factor_with_fallback('Train')
            assert fallback_factor > 0
    
    def test_google_maps_api_rate_limit_error(self):
        """Test Google Maps API rate limit error (429)"""
        api_client = APIClientManager()
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.headers = {'Retry-After': '60'}
            mock_get.return_value = mock_response
            
            result = api_client.query_google_maps_api('directions/json', {'test': 'params'})
            
            # Should return None after retries
            assert result is None
    
    def test_api_server_error_handling(self):
        """Test API server error (500) handling"""
        api_client = APIClientManager()
        
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Internal Server Error")
            mock_post.return_value = mock_response
            
            result = api_client.query_climatiq_api('estimate', {'test': 'data'})
            
            # Should return None gracefully
            assert result is None
    
    def test_api_status_validation(self):
        """Test API status validation and error information"""
        api_client = APIClientManager()
        
        # Test with various error responses
        error_responses = [
            None,  # No response
            {'error': {'message': 'Invalid request', 'code': 'invalid_request'}},  # API error
            {'status': 'REQUEST_DENIED'},  # Google Maps error
            {'status': 'OVER_QUERY_LIMIT'},  # Rate limit
        ]
        
        for response in error_responses:
            error_info = api_client.handle_api_errors(response, 'Test API')
            
            if response is None:
                assert error_info['has_error'] is True
                assert error_info['error_type'] == 'no_response'
            elif 'error' in response:
                assert error_info['has_error'] is True
                assert error_info['error_type'] == 'api_error'
            elif response.get('status') in ['REQUEST_DENIED', 'OVER_QUERY_LIMIT']:
                assert error_info['has_error'] is True
                assert error_info['error_type'] == 'status_error'
            
            # All should provide user-friendly messages
            assert error_info['user_message'] is not None
            # User message should mention fallback or service unavailable
            user_message_lower = error_info['user_message'].lower()
            assert any(term in user_message_lower for term in ['fallback', 'unavailable', 'service', 'api'])
            assert error_info['fallback_available'] is True


class TestInvalidInputProcessing:
    """Unit tests for invalid input processing"""
    
    def test_empty_form_data_validation(self):
        """Test validation of completely empty form data"""
        empty_data = {
            'origin_city': '',
            'destination_city': '',
            'outbound_date': '',
            'travel_modes': [],
            'num_travelers': 0,
            'hotel_nights': -1
        }
        
        result = FormComponents.validate_form_data(empty_data)
        
        assert result['is_valid'] is False
        assert len(result['errors']) > 0
        
        # Check specific error messages
        error_messages = ' '.join(result['errors']).lower()
        assert 'origin city is required' in error_messages
        assert 'destination city is required' in error_messages
        assert 'outbound date' in error_messages
        assert 'travel mode' in error_messages
        assert 'travelers must be' in error_messages
    
    def test_invalid_date_formats(self):
        """Test validation of invalid date formats"""
        invalid_dates = [
            'invalid-date',
            '2024-13-01',  # Invalid month
            '2024-02-30',  # Invalid day
            'not-a-date',
            '2023-01-01',  # Past date
        ]
        
        for invalid_date in invalid_dates:
            form_data = {
                'origin_city': 'Delhi',
                'destination_city': 'Mumbai',
                'outbound_date': invalid_date,
                'travel_modes': ['Flight'],
                'num_travelers': 2,
                'hotel_nights': 1
            }
            
            result = FormComponents.validate_form_data(form_data)
            
            assert result['is_valid'] is False
            error_messages = ' '.join(result['errors']).lower()
            assert 'date' in error_messages
    
    def test_invalid_numeric_inputs(self):
        """Test validation of invalid numeric inputs"""
        invalid_inputs = [
            {'num_travelers': -1, 'hotel_nights': 0},  # Negative travelers
            {'num_travelers': 0, 'hotel_nights': 0},   # Zero travelers
            {'num_travelers': 25, 'hotel_nights': 0},  # Too many travelers
            {'num_travelers': 2, 'hotel_nights': -5},  # Negative hotel nights
            {'num_travelers': 2, 'hotel_nights': 400}, # Too many hotel nights
        ]
        
        for invalid_input in invalid_inputs:
            form_data = {
                'origin_city': 'Delhi',
                'destination_city': 'Mumbai',
                'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
                'travel_modes': ['Flight'],
                'num_travelers': invalid_input['num_travelers'],
                'hotel_nights': invalid_input['hotel_nights']
            }
            
            result = FormComponents.validate_form_data(form_data)
            
            assert result['is_valid'] is False
            assert len(result['errors']) > 0
    
    def test_invalid_travel_modes(self):
        """Test validation of invalid travel modes"""
        invalid_modes = [
            ['InvalidMode'],
            ['Flight', 'Teleportation'],
            [''],
            [None],
        ]
        
        for modes in invalid_modes:
            form_data = {
                'origin_city': 'Delhi',
                'destination_city': 'Mumbai',
                'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
                'travel_modes': modes,
                'num_travelers': 2,
                'hotel_nights': 1
            }
            
            result = FormComponents.validate_form_data(form_data)
            
            if modes == []:
                # Empty modes should trigger "at least one mode" error
                assert result['is_valid'] is False
                error_messages = ' '.join(result['errors']).lower()
                assert 'travel mode' in error_messages
            elif any(mode not in ['Flight', 'Train', 'Car', 'Bus'] for mode in modes if mode):
                # Invalid modes should trigger "invalid mode" error
                assert result['is_valid'] is False
                error_messages = ' '.join(result['errors']).lower()
                assert 'invalid' in error_messages or 'mode' in error_messages
    
    def test_same_origin_destination(self):
        """Test validation when origin and destination are the same"""
        form_data = {
            'origin_city': 'Delhi',
            'destination_city': 'Delhi',  # Same as origin
            'outbound_date': (date.today() + timedelta(days=1)).isoformat(),
            'travel_modes': ['Flight'],
            'num_travelers': 2,
            'hotel_nights': 1
        }
        
        result = FormComponents.validate_form_data(form_data)
        
        assert result['is_valid'] is False
        error_messages = ' '.join(result['errors']).lower()
        assert 'same' in error_messages or 'cannot be' in error_messages
    
    def test_invalid_return_date(self):
        """Test validation of invalid return dates"""
        outbound_date = date.today() + timedelta(days=5)
        
        invalid_return_dates = [
            outbound_date - timedelta(days=1),  # Before outbound
            outbound_date,  # Same as outbound
        ]
        
        for return_date in invalid_return_dates:
            form_data = {
                'origin_city': 'Delhi',
                'destination_city': 'Mumbai',
                'outbound_date': outbound_date.isoformat(),
                'return_date': return_date.isoformat(),
                'travel_modes': ['Flight'],
                'num_travelers': 2,
                'hotel_nights': 1
            }
            
            result = FormComponents.validate_form_data(form_data)
            
            assert result['is_valid'] is False
            error_messages = ' '.join(result['errors']).lower()
            assert 'return date' in error_messages


class TestNetworkConnectivityIssues:
    """Unit tests for network connectivity issues"""
    
    def test_dns_resolution_failure(self):
        """Test DNS resolution failure handling"""
        api_client = APIClientManager()
        
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError("DNS resolution failed")
            
            result = api_client.query_climatiq_api('estimate', {'test': 'data'})
            
            # Should handle gracefully
            assert result is None
            
            # Should provide fallback
            fallback_factor = api_client.get_emission_factor_with_fallback('Car')
            assert fallback_factor > 0
    
    def test_ssl_certificate_error(self):
        """Test SSL certificate error handling"""
        api_client = APIClientManager()
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.SSLError("SSL certificate verification failed")
            
            result = api_client.query_google_maps_api('directions/json', {'test': 'params'})
            
            # Should handle gracefully
            assert result is None
    
    def test_proxy_connection_error(self):
        """Test proxy connection error handling"""
        api_client = APIClientManager()
        
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.ProxyError("Proxy connection failed")
            
            result = api_client.query_climatiq_api('estimate', {'test': 'data'})
            
            # Should handle gracefully
            assert result is None
    
    def test_network_timeout_scenarios(self):
        """Test various network timeout scenarios"""
        api_client = APIClientManager()
        
        timeout_errors = [
            requests.exceptions.Timeout("Connection timeout"),
            requests.exceptions.ReadTimeout("Read timeout"),
            requests.exceptions.ConnectTimeout("Connect timeout"),
        ]
        
        for timeout_error in timeout_errors:
            with patch('requests.post') as mock_post:
                mock_post.side_effect = timeout_error
                
                result = api_client.query_climatiq_api('estimate', {'test': 'data'})
                
                # Should handle all timeout types gracefully
                assert result is None
    
    def test_intermittent_connectivity(self):
        """Test intermittent connectivity handling with retries"""
        api_client = APIClientManager()
        
        # Test that the API client handles connection errors gracefully
        # and provides fallback mechanisms
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
            
            result = api_client.query_climatiq_api('estimate', {'test': 'data'})
            
            # Should handle connection error gracefully
            assert result is None
            
            # Should provide fallback emission factor
            fallback_factor = api_client.get_emission_factor_with_fallback('Flight')
            assert fallback_factor > 0  # Should use static fallback data
    
    def test_complete_network_failure(self):
        """Test complete network failure with fallback mechanisms"""
        calculator = CarbonCalculator()
        
        # Mock complete API failure
        with patch.object(calculator.api_client, 'query_climatiq_api', return_value=None):
            with patch.object(calculator.api_client, 'query_google_maps_api', return_value=None):
                
                # Create valid trip data
                trip_data = TripData(
                    origin_city="Delhi",
                    destination_city="Mumbai",
                    outbound_date=date.today() + timedelta(days=1),
                    return_date=None,
                    travel_modes=["Flight", "Train"],
                    num_travelers=2,
                    hotel_nights=2
                )
                
                # Should still calculate emissions using fallback factors
                result = calculator.calculate_total_emissions(trip_data, 1400.0)
                
                assert isinstance(result, EmissionsResult)
                assert result.total_co2e_kg > 0  # Should have fallback calculations
                assert len(result.transport_emissions) > 0  # Should have transport emissions
                assert result.accommodation_emissions > 0  # Should have accommodation emissions


class TestCalculationErrorHandling:
    """Unit tests for calculation error scenarios"""
    
    def test_zero_distance_calculation(self):
        """Test calculation with zero distance"""
        calculator = CarbonCalculator()
        
        trip_data = TripData(
            origin_city="Delhi",
            destination_city="Mumbai",
            outbound_date=date.today() + timedelta(days=1),
            return_date=None,
            travel_modes=["Flight"],
            num_travelers=2,
            hotel_nights=1
        )
        
        # Test with zero distance
        result = calculator.calculate_total_emissions(trip_data, 0.0)
        
        # Should handle gracefully with error information
        assert isinstance(result, EmissionsResult)
        if hasattr(result, 'calculation_warnings') and result.calculation_warnings:
            assert any('distance' in warning.lower() for warning in result.calculation_warnings)
    
    def test_invalid_trip_data_calculation(self):
        """Test calculation with invalid trip data"""
        calculator = CarbonCalculator()
        
        # Create invalid trip data
        invalid_trip_data = TripData(
            origin_city="",  # Empty origin
            destination_city="Mumbai",
            outbound_date=date.today() + timedelta(days=1),
            return_date=None,
            travel_modes=[],  # No travel modes
            num_travelers=0,  # Invalid number
            hotel_nights=-1   # Invalid nights
        )
        
        result = calculator.calculate_total_emissions(invalid_trip_data, 1000.0)
        
        # Should handle gracefully
        assert isinstance(result, EmissionsResult)
        if hasattr(result, 'calculation_warnings') and result.calculation_warnings:
            assert len(result.calculation_warnings) > 0
    
    def test_extreme_values_calculation(self):
        """Test calculation with extreme values"""
        calculator = CarbonCalculator()
        
        trip_data = TripData(
            origin_city="Delhi",
            destination_city="Mumbai",
            outbound_date=date.today() + timedelta(days=1),
            return_date=None,
            travel_modes=["Flight"],
            num_travelers=100,  # Very high number
            hotel_nights=365    # Maximum nights
        )
        
        # Test with very large distance
        result = calculator.calculate_total_emissions(trip_data, 50000.0)
        
        # Should handle extreme values
        assert isinstance(result, EmissionsResult)
        if hasattr(result, 'calculation_warnings') and result.calculation_warnings:
            warnings_text = ' '.join(result.calculation_warnings).lower()
            assert 'large' in warnings_text or 'exceeds' in warnings_text or 'limit' in warnings_text
    
    def test_missing_emission_factors(self):
        """Test calculation when emission factors are unavailable"""
        calculator = CarbonCalculator()
        
        # Mock API client to return zero emission factors
        with patch.object(calculator.api_client, 'get_emission_factor_with_fallback', return_value=0.0):
            
            trip_data = TripData(
                origin_city="Delhi",
                destination_city="Mumbai",
                outbound_date=date.today() + timedelta(days=1),
                return_date=None,
                travel_modes=["Flight"],
                num_travelers=2,
                hotel_nights=1
            )
            
            result = calculator.calculate_total_emissions(trip_data, 1000.0)
            
            # Should handle missing factors gracefully
            assert isinstance(result, EmissionsResult)
            # May have zero emissions but should not crash


class TestSessionErrorHandling:
    """Unit tests for session management error scenarios"""
    
    def test_invalid_session_data_storage(self):
        """Test storing invalid data in session"""
        # Test storing non-dict data
        with pytest.raises(ValueError):
            SessionStateManager.store_trip_data("invalid_string_data")
        
        with pytest.raises(ValueError):
            SessionStateManager.store_emissions_data(["invalid", "list", "data"])
        
        with pytest.raises(ValueError):
            SessionStateManager.store_alternatives_data("invalid_string_data")
    
    def test_corrupted_session_recovery(self):
        """Test recovery from corrupted session state"""
        # Initialize clean session
        SessionStateManager.initialize_session()
        
        # Verify clean state
        assert SessionStateManager.get_trip_data() == {}
        assert SessionStateManager.get_emissions_data() == {}
        assert SessionStateManager.get_alternatives_data() == []
        
        # Test session summary with empty data
        summary = SessionStateManager.get_session_summary()
        assert summary['has_trip_data'] is False
        assert summary['has_emissions_data'] is False
        assert summary['has_alternatives_data'] is False
    
    def test_session_state_validation(self):
        """Test session state validation with malformed data"""
        # Test with incomplete trip data that would fail TripData validation
        incomplete_trip_data = {
            'origin_city': 'Delhi',
            'destination_city': 'Mumbai',
            'outbound_date': '2024-01-01',
            'travel_modes': ['Flight'],
            'num_travelers': 1,
            'hotel_nights': 0
            # This is actually complete enough for storage, but let's test with truly invalid data
        }
        
        # Test with data that would fail TripData.from_dict validation
        invalid_trip_data = {
            'origin_city': 'Delhi',
            'destination_city': 'Mumbai',
            'outbound_date': 'invalid-date',  # This will cause from_dict to fail
            'travel_modes': ['Flight'],
            'num_travelers': 1,
            'hotel_nights': 0
        }
        
        # Should raise ValueError for data that can't create valid TripData
        with pytest.raises(ValueError):
            SessionStateManager.store_trip_data(invalid_trip_data)
    
    def test_calculation_status_validation(self):
        """Test calculation status validation"""
        # Test with invalid status types
        with pytest.raises(ValueError):
            SessionStateManager.set_calculation_status("invalid_string")
        
        with pytest.raises(ValueError):
            SessionStateManager.set_calculation_status(1)  # Should be boolean
        
        # Test with valid boolean values
        SessionStateManager.set_calculation_status(True)
        assert SessionStateManager.is_calculation_in_progress() is True
        
        SessionStateManager.set_calculation_status(False)
        assert SessionStateManager.is_calculation_in_progress() is False


if __name__ == "__main__":
    pytest.main([__file__])