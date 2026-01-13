"""
Unit tests for chart generation components

Tests chart creation with various data inputs and benchmark comparison calculations.
**Validates: Requirements 3.1, 3.2, 3.3**
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
import plotly.graph_objects as go

# Import components to test
from components.ui_components import VisualizationComponents


class TestEmissionsPieChart:
    """Unit tests for emissions pie chart generation"""
    
    def test_pie_chart_with_transport_and_accommodation(self):
        """
        Test pie chart creation with both transport and accommodation emissions
        **Validates: Requirements 3.1**
        """
        emissions_data = {
            'transport_emissions': {'Flight': 80.0, 'Train': 20.0},
            'accommodation_emissions': 30.0,
            'total_co2e_kg': 130.0
        }
        
        with patch('streamlit.plotly_chart') as mock_plotly_chart:
            VisualizationComponents._render_emissions_pie_chart(emissions_data)
            
            # Verify plotly chart was called
            mock_plotly_chart.assert_called_once()
            
            # Get the figure that was passed to plotly_chart
            call_args = mock_plotly_chart.call_args
            fig = call_args[0][0]  # First positional argument
            
            # Verify it's a plotly figure
            assert isinstance(fig, go.Figure)
            
            # Verify pie chart data
            pie_data = fig.data[0]
            assert pie_data.type == 'pie'
            
            # Should have 2 slices: Transportation and Accommodation
            assert len(pie_data.labels) == 2
            assert 'Transportation' in pie_data.labels
            assert 'Accommodation' in pie_data.labels
            
            # Verify values match expected totals
            transport_total = 100.0  # 80 + 20
            accommodation_total = 30.0
            expected_values = [transport_total, accommodation_total]
            
            assert list(pie_data.values) == expected_values
    
    def test_pie_chart_transport_only(self):
        """
        Test pie chart creation with only transport emissions
        **Validates: Requirements 3.1**
        """
        emissions_data = {
            'transport_emissions': {'Flight': 150.0},
            'accommodation_emissions': 0.0,
            'total_co2e_kg': 150.0
        }
        
        with patch('streamlit.plotly_chart') as mock_plotly_chart:
            VisualizationComponents._render_emissions_pie_chart(emissions_data)
            
            mock_plotly_chart.assert_called_once()
            fig = mock_plotly_chart.call_args[0][0]
            pie_data = fig.data[0]
            
            # Should have only 1 slice: Transportation
            assert len(pie_data.labels) == 1
            assert pie_data.labels[0] == 'Transportation'
            assert pie_data.values[0] == 150.0
    
    def test_pie_chart_accommodation_only(self):
        """
        Test pie chart creation with only accommodation emissions
        **Validates: Requirements 3.1**
        """
        emissions_data = {
            'transport_emissions': {},
            'accommodation_emissions': 75.0,
            'total_co2e_kg': 75.0
        }
        
        with patch('streamlit.plotly_chart') as mock_plotly_chart:
            VisualizationComponents._render_emissions_pie_chart(emissions_data)
            
            mock_plotly_chart.assert_called_once()
            fig = mock_plotly_chart.call_args[0][0]
            pie_data = fig.data[0]
            
            # Should have only 1 slice: Accommodation
            assert len(pie_data.labels) == 1
            assert pie_data.labels[0] == 'Accommodation'
            assert pie_data.values[0] == 75.0
    
    def test_pie_chart_no_emissions(self):
        """
        Test pie chart handling when no emissions data is available
        **Validates: Requirements 3.1**
        """
        emissions_data = {
            'transport_emissions': {},
            'accommodation_emissions': 0.0,
            'total_co2e_kg': 0.0
        }
        
        with patch('streamlit.info') as mock_info:
            VisualizationComponents._render_emissions_pie_chart(emissions_data)
            
            # Should display info message instead of chart
            mock_info.assert_called_once_with("No emissions data available for breakdown")
    
    def test_pie_chart_multiple_transport_modes(self):
        """
        Test pie chart with multiple transportation modes
        **Validates: Requirements 3.1**
        """
        emissions_data = {
            'transport_emissions': {
                'Flight': 120.0,
                'Train': 30.0,
                'Car': 25.0,
                'Bus': 15.0
            },
            'accommodation_emissions': 40.0,
            'total_co2e_kg': 230.0
        }
        
        with patch('streamlit.plotly_chart') as mock_plotly_chart:
            VisualizationComponents._render_emissions_pie_chart(emissions_data)
            
            mock_plotly_chart.assert_called_once()
            fig = mock_plotly_chart.call_args[0][0]
            pie_data = fig.data[0]
            
            # Should aggregate all transport modes into single slice
            assert len(pie_data.labels) == 2
            assert 'Transportation' in pie_data.labels
            assert 'Accommodation' in pie_data.labels
            
            # Transport total should be sum of all modes
            transport_total = 120.0 + 30.0 + 25.0 + 15.0  # 190.0
            expected_values = [transport_total, 40.0]
            assert list(pie_data.values) == expected_values


class TestBenchmarkComparison:
    """Unit tests for benchmark comparison chart generation"""
    
    def test_benchmark_comparison_chart_creation(self):
        """
        Test benchmark comparison bar chart creation with valid data
        **Validates: Requirements 3.2**
        """
        emissions_data = {
            'per_person_emissions': 120.0,
            'total_co2e_kg': 240.0
        }
        
        with patch('streamlit.plotly_chart') as mock_plotly_chart:
            VisualizationComponents._render_benchmark_comparison(emissions_data)
            
            mock_plotly_chart.assert_called_once()
            fig = mock_plotly_chart.call_args[0][0]
            
            # Verify it's a plotly figure with bar chart
            assert isinstance(fig, go.Figure)
            bar_data = fig.data[0]
            assert bar_data.type == 'bar'
            
            # Should include all benchmark categories plus user's trip
            expected_categories = [
                'Short Distance (< 500km)',
                'Medium Distance (500-1500km)', 
                'Long Distance (> 1500km)',
                'Average Domestic Trip',
                'Your Trip'
            ]
            
            assert list(bar_data.x) == expected_categories
            
            # User's trip value should match per_person_emissions
            user_trip_index = list(bar_data.x).index('Your Trip')
            assert bar_data.y[user_trip_index] == 120.0
    
    def test_benchmark_comparison_calculations(self):
        """
        Test that benchmark values are correctly included in comparison
        **Validates: Requirements 3.2**
        """
        emissions_data = {
            'per_person_emissions': 200.0,
            'total_co2e_kg': 400.0
        }
        
        with patch('streamlit.plotly_chart') as mock_plotly_chart:
            VisualizationComponents._render_benchmark_comparison(emissions_data)
            
            fig = mock_plotly_chart.call_args[0][0]
            bar_data = fig.data[0]
            
            # Verify benchmark values are included
            expected_benchmarks = {
                'Short Distance (< 500km)': 45.0,
                'Medium Distance (500-1500km)': 120.0,
                'Long Distance (> 1500km)': 280.0,
                'Average Domestic Trip': 150.0,
                'Your Trip': 200.0
            }
            
            for i, category in enumerate(bar_data.x):
                expected_value = expected_benchmarks[category]
                assert bar_data.y[i] == expected_value
    
    def test_benchmark_comparison_color_coding(self):
        """
        Test that bar chart uses appropriate color coding
        **Validates: Requirements 3.2**
        """
        emissions_data = {
            'per_person_emissions': 150.0,  # Equal to average
            'total_co2e_kg': 300.0
        }
        
        with patch('streamlit.plotly_chart') as mock_plotly_chart:
            VisualizationComponents._render_benchmark_comparison(emissions_data)
            
            fig = mock_plotly_chart.call_args[0][0]
            bar_data = fig.data[0]
            
            # Should have color array with 5 colors (one for each bar)
            assert len(bar_data.marker.color) == 5
            
            # User's trip should be blue (#1f77b4)
            user_trip_index = list(bar_data.x).index('Your Trip')
            assert bar_data.marker.color[user_trip_index] == '#1f77b4'
    
    def test_benchmark_comparison_no_emissions(self):
        """
        Test benchmark comparison handling when no per-person emissions available
        **Validates: Requirements 3.2**
        """
        emissions_data = {
            'per_person_emissions': 0.0,
            'total_co2e_kg': 0.0
        }
        
        with patch('streamlit.info') as mock_info:
            VisualizationComponents._render_benchmark_comparison(emissions_data)
            
            # Should display info message instead of chart
            mock_info.assert_called_once_with("No per-person emissions data available for comparison")
    
    def test_benchmark_comparison_negative_emissions(self):
        """
        Test benchmark comparison with negative emissions (edge case)
        **Validates: Requirements 3.2**
        """
        emissions_data = {
            'per_person_emissions': -10.0,  # Invalid negative value
            'total_co2e_kg': -20.0
        }
        
        with patch('streamlit.info') as mock_info:
            VisualizationComponents._render_benchmark_comparison(emissions_data)
            
            # Should display info message for invalid data
            mock_info.assert_called_once_with("No per-person emissions data available for comparison")


class TestChartConfiguration:
    """Unit tests for chart configuration and styling"""
    
    def test_pie_chart_styling_configuration(self):
        """
        Test that pie chart has proper styling and configuration
        **Validates: Requirements 3.1**
        """
        emissions_data = {
            'transport_emissions': {'Flight': 100.0},
            'accommodation_emissions': 50.0,
            'total_co2e_kg': 150.0
        }
        
        with patch('streamlit.plotly_chart') as mock_plotly_chart:
            VisualizationComponents._render_emissions_pie_chart(emissions_data)
            
            fig = mock_plotly_chart.call_args[0][0]
            pie_data = fig.data[0]
            
            # Verify donut chart style (hole > 0)
            assert pie_data.hole == 0.4
            
            # Verify text information includes label, percent, and value
            assert 'label+percent+value' in pie_data.textinfo
            
            # Verify colors are set
            assert pie_data.marker.colors is not None
            assert len(pie_data.marker.colors) == len(pie_data.labels)
    
    def test_bar_chart_styling_configuration(self):
        """
        Test that bar chart has proper styling and configuration
        **Validates: Requirements 3.2**
        """
        emissions_data = {
            'per_person_emissions': 100.0,
            'total_co2e_kg': 200.0
        }
        
        with patch('streamlit.plotly_chart') as mock_plotly_chart:
            VisualizationComponents._render_benchmark_comparison(emissions_data)
            
            fig = mock_plotly_chart.call_args[0][0]
            
            # Verify layout configuration
            layout = fig.layout
            assert 'Benchmark Comparison' in layout.title.text
            assert layout.xaxis.title.text == 'Trip Category'
            assert layout.yaxis.title.text == 'CO₂e Emissions (kg)'
            
            # Verify chart dimensions
            assert layout.height == 350
    
    def test_chart_hover_templates(self):
        """
        Test that charts have proper hover templates for interactivity
        **Validates: Requirements 3.1, 3.2**
        """
        emissions_data = {
            'transport_emissions': {'Flight': 80.0},
            'accommodation_emissions': 20.0,
            'per_person_emissions': 100.0,
            'total_co2e_kg': 100.0
        }
        
        with patch('streamlit.plotly_chart') as mock_plotly_chart:
            # Test pie chart hover template
            VisualizationComponents._render_emissions_pie_chart(emissions_data)
            
            fig = mock_plotly_chart.call_args[0][0]
            pie_data = fig.data[0]
            
            # Should have hover template
            assert pie_data.hovertemplate is not None
            assert '%{label}' in pie_data.hovertemplate
            assert '%{value:.2f}' in pie_data.hovertemplate
            
            # Test bar chart hover template
            VisualizationComponents._render_benchmark_comparison(emissions_data)
            
            fig = mock_plotly_chart.call_args[0][0]
            bar_data = fig.data[0]
            
            # Should have hover template
            assert bar_data.hovertemplate is not None
            assert '%{x}' in bar_data.hovertemplate
            assert '%{y:.2f}' in bar_data.hovertemplate


class TestChartDataHandling:
    """Unit tests for chart data handling edge cases"""
    
    def test_missing_data_fields(self):
        """
        Test chart generation with missing data fields
        **Validates: Requirements 3.1, 3.2**
        """
        # Test pie chart with missing fields
        incomplete_data = {'total_co2e_kg': 100.0}  # Missing transport/accommodation
        
        with patch('streamlit.info') as mock_info:
            VisualizationComponents._render_emissions_pie_chart(incomplete_data)
            # Should handle gracefully
            mock_info.assert_called_once()
        
        # Test benchmark chart with missing fields
        with patch('streamlit.info') as mock_info:
            VisualizationComponents._render_benchmark_comparison(incomplete_data)
            # Should handle gracefully
            mock_info.assert_called_once()
    
    def test_very_small_emissions_values(self):
        """
        Test chart generation with very small emission values
        **Validates: Requirements 3.1, 3.2**
        """
        emissions_data = {
            'transport_emissions': {'Train': 0.001},
            'accommodation_emissions': 0.002,
            'per_person_emissions': 0.003,
            'total_co2e_kg': 0.003
        }
        
        with patch('streamlit.plotly_chart') as mock_plotly_chart:
            # Should handle small values without errors
            VisualizationComponents._render_emissions_pie_chart(emissions_data)
            mock_plotly_chart.assert_called_once()
            
            VisualizationComponents._render_benchmark_comparison(emissions_data)
            assert mock_plotly_chart.call_count == 2
    
    def test_very_large_emissions_values(self):
        """
        Test chart generation with very large emission values
        **Validates: Requirements 3.1, 3.2**
        """
        emissions_data = {
            'transport_emissions': {'Flight': 10000.0},
            'accommodation_emissions': 5000.0,
            'per_person_emissions': 15000.0,
            'total_co2e_kg': 15000.0
        }
        
        with patch('streamlit.plotly_chart') as mock_plotly_chart:
            # Should handle large values without errors
            VisualizationComponents._render_emissions_pie_chart(emissions_data)
            mock_plotly_chart.assert_called_once()
            
            VisualizationComponents._render_benchmark_comparison(emissions_data)
            assert mock_plotly_chart.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__])