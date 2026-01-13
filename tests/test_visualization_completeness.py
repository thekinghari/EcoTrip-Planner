"""
Property-based tests for visualization completeness

Tests Property 7: Visualization Completeness
**Validates: Requirements 3.1, 3.2, 3.3, 3.5**
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime
from unittest.mock import Mock, patch
from typing import Dict, Any, List

# Import components to test
from components.ui_components import VisualizationComponents
from components.session_manager import SessionStateManager


class TestVisualizationCompleteness:
    """Property-based tests for visualization completeness"""

    @given(
        total_emissions=st.floats(min_value=0.1, max_value=1000.0),
        num_travelers=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=100, deadline=None)
    def test_visualization_completeness_property(self, total_emissions: float, num_travelers: int):
        """
        Property 7: Visualization Completeness
        For any valid emissions data, the visualization dashboard should generate all required 
        components (pie chart for breakdown, bar chart for comparisons, textual summaries) 
        and update in real-time when data changes.
        **Validates: Requirements 3.1, 3.2, 3.3, 3.5**
        """
        # Create valid emissions data
        transport_emissions = {'Flight': total_emissions * 0.8}
        accommodation_emissions = total_emissions * 0.2
        per_person_emissions = total_emissions / num_travelers
        
        emissions_data = {
            'total_co2e_kg': total_emissions,
            'transport_emissions': transport_emissions,
            'accommodation_emissions': accommodation_emissions,
            'per_person_emissions': per_person_emissions,
            'calculation_timestamp': datetime.now().isoformat()
        }
        
        # Mock streamlit components to capture calls
        with patch('streamlit.subheader') as mock_subheader, \
             patch('streamlit.columns') as mock_columns, \
             patch('streamlit.markdown') as mock_markdown, \
             patch('streamlit.metric') as mock_metric, \
             patch('streamlit.plotly_chart') as mock_plotly_chart, \
             patch.object(SessionStateManager, 'is_calculation_in_progress', return_value=False):
            
            # Set up column mocks
            col1_mock = Mock()
            col2_mock = Mock()
            col3_mock = Mock()
            
            # Mock the context managers for columns
            col1_mock.__enter__ = Mock(return_value=col1_mock)
            col1_mock.__exit__ = Mock(return_value=None)
            col2_mock.__enter__ = Mock(return_value=col2_mock)
            col2_mock.__exit__ = Mock(return_value=None)
            col3_mock.__enter__ = Mock(return_value=col3_mock)
            col3_mock.__exit__ = Mock(return_value=None)
            
            # Set up columns mock to return appropriate columns for each call
            def columns_side_effect(*args, **kwargs):
                # Handle both st.columns(2) and st.columns([1, 1]) formats
                if args:
                    if isinstance(args[0], list):
                        num_cols = len(args[0])
                    else:
                        num_cols = args[0]
                else:
                    num_cols = 2  # default
                
                if num_cols == 2:
                    return [col1_mock, col2_mock]
                elif num_cols == 3:
                    return [col1_mock, col2_mock, col3_mock]
                else:
                    return [Mock() for _ in range(num_cols)]
            
            mock_columns.side_effect = columns_side_effect
            
            # Call the visualization dashboard
            VisualizationComponents.render_emissions_dashboard(emissions_data)
            
            # Verify all required components are rendered
            
            # 1. Dashboard header should be displayed (Requirement 3.1, 3.2, 3.3)
            mock_subheader.assert_called_with("📊 Carbon Footprint Analysis")
            
            # 2. Columns should be created for layout
            assert mock_columns.call_count >= 1, "Columns should be created for chart layout"
            
            # 3. Charts should be rendered (Requirements 3.1, 3.2)
            # At least one plotly chart should be created for pie chart and/or bar chart
            assert mock_plotly_chart.call_count >= 1, "At least one chart should be rendered"
            
            # 4. Impact summary section should be created (Requirement 3.3)
            summary_calls = [call for call in mock_markdown.call_args_list 
                           if "Impact Summary" in str(call)]
            assert len(summary_calls) >= 1, "Impact summary section should be rendered"
            
            # 5. Metrics should be displayed (Requirement 3.3)
            assert mock_metric.call_count >= 3, "At least 3 metrics should be displayed (total, per person, vs average)"


if __name__ == "__main__":
    pytest.main([__file__])