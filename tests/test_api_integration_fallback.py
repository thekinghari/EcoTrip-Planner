"""
Property-based tests for API integration with fallback

Feature: ecotrip-planner, Property 4: API Integration with Fallback
Validates: Requirements 2.1, 2.2, 6.2, 6.4, 6.5
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import Mock, patch, MagicMock
import requests
import sys
import os

# Add the project root to the path so we can import components
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.api_client import APIClientManager


class TestAPIIntegrationWithFallback:
    """Property-based tests for API integration with fallback mechanisms"""
    
    def setup_method(self):
        """Set up test environment"""
        # Mock API key for testing
        with patch.dict(os.environ, {'CLIMATIQ_API_KEY': 'test_key'}):
            self.api_client = APIClientManager()
    
    @given(st.sampled_from(['Flight', 'Train', 'Car', 'Bus', 'Hotel']))
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_api_fallback_mechanism(self, transport_mode):
        """
        Property 4: API Integration with Fallback
        For any transport mode, when API is unavailable, system should fall back to static data
        """
        # Mock API failure scenarios
        with patch.object(self.api_client, 'query_climatiq_api', return_value=None):
            # Should return static emission factor when API fails
            emission_factor = self.api_client.get_emission_factor_with_fallback(transport_mode)
            
            # Should always return a valid emission factor (fallback)
            assert emission_factor is not None
            assert emission_factor >= 0.0
            
            # Should match static emission factors
            expected_factor = self.api_client.static_emission_factors.get(transport_mode, 0.0)
            assert emission_factor == expected_factor
    
    @given(st.sampled_from(['Flight', 'Train', 'Car', 'Bus']))
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_api_success_returns_api_data(self, transport_mode):
        """
        Property 4: API Integration with Fallback
        For any transport mode, when API is available, system should use API data
        """
        # Mock successful API response
        mock_response = {'co2e': 0.123}
        
        with patch.object(self.api_client, 'query_climatiq_api', return_value=mock_response):
            emission_factor = self.api_client.get_emission_factor_with_fallback(transport_mode)
            
            # Should return API data when available
            assert emission_factor == 0.123
    
    @given(st.integers(min_value=1, max_value=5))
    def test_retry_logic_exhaustion(self, max_retries):
        """
        Property 4: API Integration with Fallback
        For any number of retries, system should eventually give up and return None
        """
        # Mock persistent API failure
        with patch('requests.post', side_effect=requests.exceptions.ConnectionError()):
            result = self.api_client.query_climatiq_api('test', {}, max_retries=max_retries)
            
            # Should return None after exhausting retries
            assert result is None
    
    @given(st.integers(min_value=1, max_value=5))
    @settings(deadline=None)
    def test_retry_logic_eventual_success(self, failure_count):
        """
        Property 4: API Integration with Fallback
        For any number of initial failures, system should succeed when API becomes available
        """
        # Mock initial failures followed by success
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'co2e': 0.456}
        mock_response.raise_for_status.return_value = None
        
        side_effects = [requests.exceptions.ConnectionError()] * failure_count + [mock_response]
        
        with patch('requests.post', side_effect=side_effects):
            result = self.api_client.query_climatiq_api('test', {}, max_retries=failure_count + 1)
            
            # Should eventually succeed
            assert result is not None
            assert result == {'co2e': 0.456}
    
    @given(st.integers(min_value=429, max_value=429))
    def test_rate_limit_handling(self, status_code):
        """
        Property 4: API Integration with Fallback
        For rate limit responses (429), system should handle gracefully
        """
        # Mock rate limit response
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.headers = {'Retry-After': '1'}
        
        with patch('requests.post', return_value=mock_response):
            with patch('time.sleep') as mock_sleep:  # Mock sleep to speed up test
                result = self.api_client.query_climatiq_api('test', {}, max_retries=1)
                
                # Should return None after rate limit
                assert result is None
    
    @given(st.text(min_size=1, max_size=50))
    def test_missing_api_key_fallback(self, endpoint):
        """
        Property 4: API Integration with Fallback
        For any endpoint, when API key is missing, system should return None
        """
        # Temporarily remove API key
        original_key = self.api_client.climatiq_api_key
        self.api_client.climatiq_api_key = None
        
        try:
            result = self.api_client.query_climatiq_api(endpoint, {})
            
            # Should return None when API key is missing
            assert result is None
        finally:
            # Restore original key
            self.api_client.climatiq_api_key = original_key
    
    @given(st.floats(min_value=0.1, max_value=10.0))
    def test_timeout_handling(self, timeout_duration):
        """
        Property 4: API Integration with Fallback
        For any timeout scenario, system should handle gracefully
        """
        # Mock timeout exception
        with patch('requests.post', side_effect=requests.exceptions.Timeout()):
            result = self.api_client.query_climatiq_api('test', {}, max_retries=1)
            
            # Should return None on timeout
            assert result is None
    
    @given(st.dictionaries(st.text(), st.text(), min_size=0, max_size=5))
    @settings(deadline=None)
    def test_malformed_response_handling(self, response_data):
        """
        Property 4: API Integration with Fallback
        For any malformed response, system should handle gracefully
        """
        # Mock response without required fields
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = response_data
        mock_response.raise_for_status.return_value = None
        
        with patch('requests.post', return_value=mock_response):
            # Should not crash on malformed response
            try:
                result = self.api_client.query_climatiq_api('test', {})
                # Result should be the response data (even if malformed)
                assert result == response_data
            except Exception:
                # Should not raise unhandled exceptions
                pytest.fail("API client should handle malformed responses gracefully")
    
    def test_error_detection_accuracy(self):
        """
        Property 4: API Integration with Fallback
        Error detection should correctly identify error conditions
        """
        # Test various error response formats
        error_responses = [
            None,  # No response
            {'error': 'Invalid request'},  # Error field
            {'status': 'REQUEST_DENIED'},  # Denied status
            {'status': 'OVER_QUERY_LIMIT'},  # Rate limit status
            {'status': 'INVALID_REQUEST'},  # Invalid request status
        ]
        
        for response in error_responses:
            assert self.api_client.handle_api_errors(response) == True
        
        # Test valid responses
        valid_responses = [
            {'co2e': 0.123},  # Valid emission data
            {'status': 'OK', 'data': 'valid'},  # OK status
            {'result': 'success'},  # Success result
        ]
        
        for response in valid_responses:
            assert self.api_client.handle_api_errors(response) == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])