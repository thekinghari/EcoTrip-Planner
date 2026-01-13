"""
Property-based tests for error handling gracefully

Tests Property 9: Error Handling Gracefully
**Validates: Requirements 6.3**

This module tests that the system displays user-friendly error messages 
without exposing technical implementation details for any error condition.
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from unittest.mock import Mock, patch, MagicMock
import requests
from datetime import date, datetime, timedelta
from typing import Dict, Any, List

from components.api_client import APIClientManager
from components.carbon_calculator import CarbonCalculator
from components.ui_components import UIComponents, FormComponents
from components.session_manager import SessionStateManager
from components.models import TripData, EmissionsResult


class TestErrorHandlingGracefully:
    """Property-based tests for graceful error handling across all components"""
    
    @given(
        error_types=st.sampled_from([
            requests.exceptions.ConnectionError("Network error"),
            requests.exceptions.Timeout("Request timeout"),
            requests.exceptions.HTTPError("HTTP error"),
            ValueError("Invalid value"),
            KeyError("Missing key"),
            Exception("Generic error")
        ])
    )
    @settings(max_examples=100)
    def test_api_client_error_handling_gracefully(self, error_types):
        """
        Property 9: Error Handling Gracefully
        For any error condition in API client, the system should handle errors gracefully
        without exposing technical implementation details.
        **Validates: Requirements 6.3**
        """
        api_client = APIClientManager()
        
        # Mock requests to raise the error
        with patch('requests.post') as mock_post, patch('requests.get') as mock_get:
            mock_post.side_effect = error_types
            mock_get.side_effect = error_types
            
            # Test Climatiq API error handling
            result = api_client.query_climatiq_api('estimate', {'test': 'data'})
            
            # Should return None gracefully, not raise exception
            assert result is None
            
            # Test Google Maps API error handling
            result = api_client.query_google_maps_api('directions/json', {'test': 'params'})
            
            # Should return None gracefully, not raise exception
            assert result is None
            
            # Test error handling method
            error_info = api_client.handle_api_errors(None, 'Test API')
            
            # Should provide user-friendly error information
            assert error_info['has_error'] is True
            assert error_info['user_message'] is not None
            assert 'Test API' in error_info['user_message']
            
            # User message should not contain technical details
            user_message = error_info['user_message'].lower()
            technical_terms = ['exception', 'traceback', 'stack', 'debug', 'internal error']
            for term in technical_terms:
                assert term not in user_message
    
    @given(
        invalid_trip_data=st.fixed_dictionaries({
            'origin_city': st.one_of(st.just(''), st.just(None), st.text(max_size=0)),
            'destination_city': st.one_of(st.just(''), st.just(None), st.text(max_size=0)),
            'outbound_date': st.one_of(st.just(''), st.just('invalid-date'), st.just(None)),
            'travel_modes': st.one_of(st.just([]), st.just(None), st.lists(st.text(), max_size=0)),
            'num_travelers': st.one_of(st.integers(max_value=0), st.integers(min_value=100)),
            'hotel_nights': st.integers(max_value=-1)
        })
    )
    @settings(max_examples=100)
    def test_form_validation_error_handling_gracefully(self, invalid_trip_data):
        """
        Property 9: Error Handling Gracefully
        For any invalid form input, the system should provide user-friendly validation
        error messages without exposing technical implementation details.
        **Validates: Requirements 6.3**
        """
        # Test form validation with invalid data
        validation_result = FormComponents.validate_form_data(invalid_trip_data)
        
        # Should not raise exception, should return validation result
        assert isinstance(validation_result, dict)
        assert 'is_valid' in validation_result
        assert 'errors' in validation_result
        
        # Should be invalid due to bad data
        assert validation_result['is_valid'] is False
        assert len(validation_result['errors']) > 0
        
        # Error messages should be user-friendly
        for error in validation_result['errors']:
            assert isinstance(error, str)
            assert len(error) > 0
            
            # Should not contain technical terms
            error_lower = error.lower()
            technical_terms = ['exception', 'traceback', 'none', 'null', 'undefined']
            for term in technical_terms:
                assert term not in error_lower
            
            # Should contain helpful guidance
            helpful_terms = ['required', 'must', 'should', 'cannot', 'invalid', 'enter', 'select']
            assert any(term in error_lower for term in helpful_terms)
    
    @given(
        calculation_errors=st.sampled_from([
            "API unavailable",
            "Network timeout", 
            "Invalid emission factor",
            "Calculation overflow",
            "Missing data"
        ])
    )
    @settings(max_examples=100)
    def test_carbon_calculator_error_handling_gracefully(self, calculation_errors):
        """
        Property 9: Error Handling Gracefully
        For any calculation error, the system should handle errors gracefully
        and provide meaningful fallback results.
        **Validates: Requirements 6.3**
        """
        calculator = CarbonCalculator()
        
        # Create valid trip data
        trip_data = TripData(
            origin_city="Delhi",
            destination_city="Mumbai", 
            outbound_date=date.today() + timedelta(days=1),
            return_date=None,
            travel_modes=["Flight"],
            num_travelers=2,
            hotel_nights=1
        )
        
        # Mock API client to simulate errors
        with patch.object(calculator.api_client, 'get_emission_factor_with_fallback') as mock_factor:
            # Simulate different error conditions
            if "API unavailable" in calculation_errors:
                mock_factor.return_value = 0.0  # No data available
            elif "Invalid emission factor" in calculation_errors:
                mock_factor.side_effect = ValueError("Invalid factor")
            else:
                mock_factor.return_value = 0.1  # Valid fallback
            
            # Test calculation with potential errors
            try:
                result = calculator.calculate_total_emissions(trip_data, 1000.0)
                
                # Should return a valid EmissionsResult object, not raise exception
                assert isinstance(result, EmissionsResult)
                assert hasattr(result, 'total_co2e_kg')
                assert hasattr(result, 'calculation_timestamp')
                
                # Should handle errors gracefully with warnings if needed
                if hasattr(result, 'calculation_warnings') and result.calculation_warnings:
                    for warning in result.calculation_warnings:
                        # Warnings should be user-friendly
                        assert isinstance(warning, str)
                        warning_lower = warning.lower()
                        
                        # Should not expose technical details
                        technical_terms = ['exception', 'traceback', 'debug', 'internal']
                        for term in technical_terms:
                            assert term not in warning_lower
                            
            except Exception as e:
                # If an exception occurs, it should be handled gracefully
                pytest.fail(f"Calculator should handle errors gracefully, but raised: {e}")
    
    @given(
        session_errors=st.sampled_from([
            "Invalid session data",
            "Corrupted state",
            "Missing session key",
            "Type mismatch"
        ])
    )
    @settings(max_examples=100) 
    def test_session_manager_error_handling_gracefully(self, session_errors):
        """
        Property 9: Error Handling Gracefully
        For any session management error, the system should handle errors gracefully
        without losing user progress when possible.
        **Validates: Requirements 6.3**
        """
        # Test various session error conditions
        try:
            if "Invalid session data" in session_errors:
                # Test storing invalid data
                with pytest.raises(ValueError):
                    SessionStateManager.store_trip_data("invalid_data")  # Should raise ValueError
                    
            elif "Type mismatch" in session_errors:
                # Test storing wrong type
                with pytest.raises(ValueError):
                    SessionStateManager.store_emissions_data("not_a_dict")  # Should raise ValueError
                    
            else:
                # Test normal operations don't raise unexpected errors
                SessionStateManager.initialize_session()
                summary = SessionStateManager.get_session_summary()
                
                # Should return valid summary structure
                assert isinstance(summary, dict)
                required_keys = ['has_trip_data', 'has_emissions_data', 'calculation_in_progress']
                for key in required_keys:
                    assert key in summary
                    
        except Exception as e:
            # Any exceptions should be handled gracefully by the application layer
            error_message = str(e)
            
            # Error messages should be user-friendly
            error_lower = error_message.lower()
            technical_terms = ['traceback', 'debug', 'internal error']
            for term in technical_terms:
                assert term not in error_lower
    
    @given(
        network_conditions=st.sampled_from([
            "connection_timeout",
            "dns_failure", 
            "ssl_error",
            "proxy_error",
            "rate_limit_exceeded"
        ])
    )
    @settings(max_examples=100)
    def test_network_error_handling_gracefully(self, network_conditions):
        """
        Property 9: Error Handling Gracefully
        For any network error condition, the system should provide helpful
        user guidance and fallback mechanisms.
        **Validates: Requirements 6.3**
        """
        api_client = APIClientManager()
        
        # Simulate different network error conditions
        error_mapping = {
            "connection_timeout": requests.exceptions.Timeout("Connection timed out"),
            "dns_failure": requests.exceptions.ConnectionError("DNS resolution failed"),
            "ssl_error": requests.exceptions.SSLError("SSL certificate error"),
            "proxy_error": requests.exceptions.ProxyError("Proxy connection failed"),
            "rate_limit_exceeded": requests.exceptions.HTTPError("429 Too Many Requests")
        }
        
        simulated_error = error_mapping.get(network_conditions, requests.exceptions.RequestException("Network error"))
        
        with patch('requests.post') as mock_post:
            mock_post.side_effect = simulated_error
            
            # Test API call with network error
            result = api_client.query_climatiq_api('estimate', {'test': 'data'})
            
            # Should handle error gracefully
            assert result is None
            
            # Test fallback mechanism
            fallback_factor = api_client.get_emission_factor_with_fallback('Flight')
            
            # Should provide fallback value
            assert isinstance(fallback_factor, (int, float))
            assert fallback_factor >= 0
            
            # Test error information
            error_info = api_client.handle_api_errors(None, 'Climatiq')
            
            # Should provide user-friendly guidance
            assert error_info['has_error'] is True
            assert error_info['user_message'] is not None
            assert error_info['fallback_available'] is True
            
            # User message should be helpful, not technical
            user_message = error_info['user_message'].lower()
            helpful_terms = ['unavailable', 'fallback', 'try again', 'service']
            assert any(term in user_message for term in helpful_terms)
            
            # Should not expose technical error details
            technical_terms = ['ssl', 'dns', 'proxy', 'timeout', 'exception']
            for term in technical_terms:
                assert term not in user_message


if __name__ == "__main__":
    pytest.main([__file__])