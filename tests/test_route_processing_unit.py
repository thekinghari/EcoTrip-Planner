"""
Unit tests for route processing and cost estimation

Tests specific examples, edge cases, and error conditions for route processing
and cost calculation accuracy for different modes.
**Validates: Requirements 4.2, 4.3**
"""

import pytest
from components.route_analyzer import RouteAnalyzer, CostEstimator
from components.models import TripData, AlternativeRoute
from datetime import date, timedelta


class TestRouteProcessingUnit:
    """Unit tests for route processing functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.route_analyzer = RouteAnalyzer()
        self.cost_estimator = CostEstimator()
    
    def test_route_data_parsing_valid_input(self):
        """Test route data parsing with valid input data"""
        # Test data representing Google Maps API response format
        routes_data = {
            'Car': [{
                'mode': 'Car',
                'distance_km': 500.0,
                'duration_hours': 8.5,
                'start_address': 'Delhi, India',
                'end_address': 'Mumbai, India',
                'steps': [
                    {
                        'distance_km': 250.0,
                        'duration_hours': 4.0,
                        'instructions': 'Head south on NH48',
                        'travel_mode': 'DRIVING'
                    }
                ],
                'polyline': 'encoded_polyline_string',
                'bounds': {'northeast': {'lat': 28.7, 'lng': 77.2}, 'southwest': {'lat': 19.1, 'lng': 72.9}},
                'warnings': [],
                'copyrights': 'Map data ©2024 Google'
            }]
        }
        
        trip_data = TripData(
            origin_city='Delhi',
            destination_city='Mumbai',
            outbound_date=date.today() + timedelta(days=1),
            return_date=None,
            travel_modes=['Car'],
            num_travelers=2,
            hotel_nights=1
        )
        
        alternatives = self.route_analyzer.process_route_data(routes_data, trip_data)
        
        assert len(alternatives) == 1
        alternative = alternatives[0]
        
        assert alternative.transport_mode == 'Car'
        assert alternative.distance_km == 500.0
        assert alternative.duration_hours == 8.5
        assert alternative.co2e_emissions_kg > 0  # Should calculate emissions
        assert alternative.estimated_cost_inr > 0  # Should calculate cost
        assert 'start_address' in alternative.route_details
        assert alternative.route_details['start_address'] == 'Delhi, India'
    
    def test_route_data_parsing_empty_input(self):
        """Test route data parsing with empty input"""
        routes_data = {}
        
        trip_data = TripData(
            origin_city='Delhi',
            destination_city='Mumbai',
            outbound_date=date.today() + timedelta(days=1),
            return_date=None,
            travel_modes=['Car'],
            num_travelers=1,
            hotel_nights=0
        )
        
        alternatives = self.route_analyzer.process_route_data(routes_data, trip_data)
        
        assert len(alternatives) == 0
    
    def test_route_data_parsing_malformed_input(self):
        """Test route data parsing with malformed input data"""
        # Missing required fields
        routes_data = {
            'Train': [{
                'mode': 'Train',
                # Missing distance_km and duration_hours
                'start_address': 'Chennai, India',
                'end_address': 'Bangalore, India'
            }]
        }
        
        trip_data = TripData(
            origin_city='Chennai',
            destination_city='Bangalore',
            outbound_date=date.today() + timedelta(days=1),
            return_date=None,
            travel_modes=['Train'],
            num_travelers=1,
            hotel_nights=0
        )
        
        # Should handle malformed data gracefully
        alternatives = self.route_analyzer.process_route_data(routes_data, trip_data)
        
        # May return empty list or handle with default values
        assert isinstance(alternatives, list)
    
    def test_route_validation_valid_data(self):
        """Test route data validation with valid input"""
        valid_route = {
            'mode': 'Bus',
            'distance_km': 300.0,
            'duration_hours': 6.0,
            'start_address': 'Pune, India',
            'end_address': 'Mumbai, India'
        }
        
        assert self.route_analyzer.validate_route_data(valid_route) == True
    
    def test_route_validation_invalid_data(self):
        """Test route data validation with invalid input"""
        # Missing required fields
        invalid_route1 = {
            'mode': 'Flight',
            # Missing distance_km and duration_hours
        }
        
        assert self.route_analyzer.validate_route_data(invalid_route1) == False
        
        # Negative values
        invalid_route2 = {
            'mode': 'Car',
            'distance_km': -100.0,
            'duration_hours': 5.0
        }
        
        assert self.route_analyzer.validate_route_data(invalid_route2) == False
        
        # Invalid mode
        invalid_route3 = {
            'mode': 'Teleportation',
            'distance_km': 500.0,
            'duration_hours': 0.1
        }
        
        assert self.route_analyzer.validate_route_data(invalid_route3) == False


class TestCostEstimationUnit:
    """Unit tests for cost estimation functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.route_analyzer = RouteAnalyzer()
        self.cost_estimator = CostEstimator()
    
    def test_cost_calculation_flight_mode(self):
        """Test cost calculation accuracy for flight mode"""
        distance_km = 1000.0
        num_travelers = 2
        
        cost = self.route_analyzer.estimate_costs('Flight', distance_km, num_travelers)
        
        # Flight cost should include base cost + distance cost
        expected_base = self.route_analyzer.base_costs['Flight'] * num_travelers
        expected_distance = distance_km * self.route_analyzer.cost_factors['Flight'] * num_travelers
        expected_total = expected_base + expected_distance
        
        assert abs(cost - expected_total) < 0.01
        assert cost > 0
        
        # Should be reasonable for Indian flight costs (₹8000-20000 for 1000km for 2 people)
        assert 8000 <= cost <= 25000
    
    def test_cost_calculation_train_mode(self):
        """Test cost calculation accuracy for train mode"""
        distance_km = 500.0
        num_travelers = 3
        
        cost = self.route_analyzer.estimate_costs('Train', distance_km, num_travelers)
        
        # Train cost should be lower than flight
        flight_cost = self.route_analyzer.estimate_costs('Flight', distance_km, num_travelers)
        assert cost < flight_cost
        
        # Should be reasonable for Indian train costs (₹600-3000 for 500km for 3 people)
        assert 600 <= cost <= 4000
    
    def test_cost_calculation_car_mode(self):
        """Test cost calculation accuracy for car mode"""
        distance_km = 300.0
        num_travelers = 4
        
        cost = self.route_analyzer.estimate_costs('Car', distance_km, num_travelers)
        
        # Car cost should scale with travelers and distance
        expected_cost = distance_km * self.route_analyzer.cost_factors['Car'] * num_travelers
        assert abs(cost - expected_cost) < 0.01  # No base cost for car
        
        # Should be reasonable for Indian car costs (₹7200 for 300km for 4 people)
        assert 5000 <= cost <= 10000
    
    def test_cost_calculation_bus_mode(self):
        """Test cost calculation accuracy for bus mode"""
        distance_km = 200.0
        num_travelers = 1
        
        cost = self.route_analyzer.estimate_costs('Bus', distance_km, num_travelers)
        
        # Bus should be cheapest option after train
        train_cost = self.route_analyzer.estimate_costs('Train', distance_km, num_travelers)
        car_cost = self.route_analyzer.estimate_costs('Car', distance_km, num_travelers)
        
        assert cost < car_cost  # Bus should be cheaper than car
        
        # Should be reasonable for Indian bus costs (₹525 for 200km for 1 person)
        assert 400 <= cost <= 800
    
    def test_cost_calculation_zero_distance(self):
        """Test cost calculation with zero distance (edge case)"""
        distance_km = 0.0
        num_travelers = 2
        
        for mode in ['Flight', 'Train', 'Car', 'Bus']:
            cost = self.route_analyzer.estimate_costs(mode, distance_km, num_travelers)
            
            # Should only include base cost for zero distance
            expected_cost = self.route_analyzer.base_costs[mode] * num_travelers
            assert abs(cost - expected_cost) < 0.01
    
    def test_cost_calculation_single_traveler(self):
        """Test cost calculation with single traveler"""
        distance_km = 400.0
        
        for mode in ['Flight', 'Train', 'Car', 'Bus']:
            cost_1 = self.route_analyzer.estimate_costs(mode, distance_km, 1)
            cost_2 = self.route_analyzer.estimate_costs(mode, distance_km, 2)
            
            # Cost should scale linearly with travelers
            assert abs(cost_2 - cost_1 * 2) < 0.01
    
    def test_cost_calculation_maximum_travelers(self):
        """Test cost calculation with maximum number of travelers"""
        distance_km = 100.0
        max_travelers = 20
        
        for mode in ['Flight', 'Train', 'Car', 'Bus']:
            cost = self.route_analyzer.estimate_costs(mode, distance_km, max_travelers)
            
            # Should handle large number of travelers
            assert cost > 0
            
            # Cost per person should be reasonable
            cost_per_person = cost / max_travelers
            assert cost_per_person > 0
    
    def test_detailed_cost_estimation_train_classes(self):
        """Test detailed cost estimation for different train classes"""
        distance_km = 600.0
        num_travelers = 2
        
        # Test different service classes
        sleeper_cost = self.cost_estimator.estimate_detailed_costs('Train', distance_km, num_travelers, 'budget')
        ac3_cost = self.cost_estimator.estimate_detailed_costs('Train', distance_km, num_travelers, 'standard')
        ac1_cost = self.cost_estimator.estimate_detailed_costs('Train', distance_km, num_travelers, 'premium')
        
        # Higher classes should cost more
        assert sleeper_cost['total'] < ac3_cost['total'] < ac1_cost['total']
        
        # All should have reasonable breakdown
        for cost_data in [sleeper_cost, ac3_cost, ac1_cost]:
            assert cost_data['total'] > 0
            assert cost_data['per_person'] > 0
            assert cost_data['base_cost'] >= 0
            assert cost_data['distance_cost'] > 0
            assert abs(cost_data['total'] - (cost_data['base_cost'] + cost_data['distance_cost'])) < 0.01
    
    def test_detailed_cost_estimation_flight_classes(self):
        """Test detailed cost estimation for different flight classes"""
        distance_km = 1200.0
        num_travelers = 1
        
        economy_cost = self.cost_estimator.estimate_detailed_costs('Flight', distance_km, num_travelers, 'standard')
        business_cost = self.cost_estimator.estimate_detailed_costs('Flight', distance_km, num_travelers, 'premium')
        
        # Business class should cost more than economy
        assert economy_cost['total'] < business_cost['total']
        
        # Both should have airport taxes (base cost)
        assert economy_cost['base_cost'] > 0
        assert business_cost['base_cost'] > 0
    
    def test_cost_estimation_edge_cases(self):
        """Test cost estimation edge cases"""
        # Very long distance
        long_distance = 3000.0
        cost_long = self.route_analyzer.estimate_costs('Flight', long_distance, 1)
        assert cost_long > 0
        
        # Very short distance
        short_distance = 10.0
        cost_short = self.route_analyzer.estimate_costs('Bus', short_distance, 1)
        assert cost_short > 0
        
        # Cost should increase with distance
        medium_distance = 500.0
        cost_medium = self.route_analyzer.estimate_costs('Car', medium_distance, 1)
        cost_short_car = self.route_analyzer.estimate_costs('Car', short_distance, 1)
        
        assert cost_medium > cost_short_car
    
    def test_cost_factors_reasonableness(self):
        """Test that cost factors are reasonable for Indian market"""
        cost_factors = self.route_analyzer.cost_factors
        
        # Flight should be most expensive per km
        assert cost_factors['Flight'] > cost_factors['Car']
        assert cost_factors['Car'] > cost_factors['Bus']
        assert cost_factors['Bus'] > cost_factors['Train']
        
        # All factors should be positive and reasonable
        for mode, factor in cost_factors.items():
            assert factor > 0
            if mode == 'Flight':
                assert 5.0 <= factor <= 15.0  # ₹5-15 per km reasonable for flights
            elif mode == 'Train':
                assert 0.5 <= factor <= 3.0   # ₹0.5-3 per km reasonable for trains
            elif mode == 'Car':
                assert 3.0 <= factor <= 10.0  # ₹3-10 per km reasonable for cars
            elif mode == 'Bus':
                assert 1.0 <= factor <= 5.0   # ₹1-5 per km reasonable for buses
    
    def test_base_costs_reasonableness(self):
        """Test that base costs are reasonable for Indian market"""
        base_costs = self.route_analyzer.base_costs
        
        # Flight should have highest base cost (airport taxes, etc.)
        assert base_costs['Flight'] > base_costs['Train']
        assert base_costs['Flight'] > base_costs['Bus']
        
        # Car should have no base cost (personal vehicle)
        assert base_costs['Car'] == 0.0
        
        # All base costs should be reasonable
        assert 200 <= base_costs['Flight'] <= 1000   # Airport taxes
        assert 0 <= base_costs['Train'] <= 200       # Reservation fees
        assert 0 <= base_costs['Bus'] <= 100         # Booking fees