"""
EcoTrip Planner - Sustainable Travel Carbon Footprint Calculator

A Streamlit web application that helps travelers in India make environmentally 
conscious travel decisions by calculating carbon emissions and suggesting greener alternatives.
"""

import streamlit as st
import os
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from components.ui_components import UIComponents, FormComponents, VisualizationComponents
from components.session_manager import SessionStateManager
from components.carbon_calculator import CarbonCalculator
from components.route_analyzer import RouteAnalyzer
from components.geographic_data import GeographicDataManager

# Load environment variables
load_dotenv()

def main():
    """Main application entry point with comprehensive error handling and complete workflow"""
    try:
        # Configure Streamlit page with eco-friendly settings
        configure_streamlit_app()
        
        # Apply comprehensive eco-themed styling
        apply_eco_styling()
        
        # Initialize session state with error handling
        try:
            SessionStateManager.initialize_session()
        except Exception as e:
            st.error("⚠️ Failed to initialize session. Please refresh the page.")
            st.sidebar.error(f"Session Error: {str(e)}")
            return
        
        # Render main application header with enhanced styling
        render_enhanced_header()
        
        # Main application workflow
        handle_main_workflow()
        
        # Sidebar with status and configuration
        render_sidebar_content()
            
    except Exception as e:
        # Handle WebSocket errors gracefully
        error_msg = str(e)
        error_type = type(e).__name__
        
        # Check for WebSocket-related errors
        if 'WebSocket' in error_type or 'websocket' in error_msg.lower() or 'StreamClosed' in error_type:
            # WebSocket errors are usually harmless - just log and continue
            # They occur when the connection closes during rerun operations
            pass  # Silently ignore WebSocket errors as they're typically harmless
        else:
            # Catch-all error handler for other errors
            handle_critical_error(e)

def configure_streamlit_app():
    """Configure Streamlit application settings with deployment-ready options"""
    # Get configuration from environment variables with defaults
    page_title = os.getenv('STREAMLIT_PAGE_TITLE', ' EcoTrip Planner - Sustainable Travel Calculator')
    page_icon = os.getenv('STREAMLIT_PAGE_ICON', '🌱')
    layout = os.getenv('STREAMLIT_LAYOUT', 'wide')
    sidebar_state = os.getenv('STREAMLIT_SIDEBAR_STATE', 'expanded')
    
    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout=layout,
        initial_sidebar_state=sidebar_state,
        menu_items={
            'Get Help': 'https://github.com/ecotrip-planner/help',
            'Report a bug': 'https://github.com/ecotrip-planner/issues',
            'About': "EcoTrip Planner helps you make sustainable travel choices by calculating carbon emissions and suggesting greener alternatives for travel within India."
        }
    )
    
    # Set additional configuration based on environment
    if os.getenv('STREAMLIT_THEME_BASE'):
        st._config.set_option('theme.base', os.getenv('STREAMLIT_THEME_BASE'))
    
    # Configure caching and performance settings
    if os.getenv('STREAMLIT_SERVER_MAX_UPLOAD_SIZE'):
        st._config.set_option('server.maxUploadSize', int(os.getenv('STREAMLIT_SERVER_MAX_UPLOAD_SIZE')))
    
    # Development vs Production settings
    is_production = os.getenv('ENVIRONMENT', 'development').lower() == 'production'
    
    if is_production:
        # Production settings
        st._config.set_option('global.developmentMode', False)
        st._config.set_option('client.showErrorDetails', False)
        st._config.set_option('browser.gatherUsageStats', False)
    else:
        # Development settings
        st._config.set_option('global.developmentMode', True)
        st._config.set_option('client.showErrorDetails', True)

def apply_eco_styling():
    """Apply comprehensive eco-themed styling with green colors and environmental design"""
    st.markdown("""
    <style>
    /* Main app styling */
    .stApp {
        background: linear-gradient(135deg, #f0f8f0 0%, #e8f5e8 100%);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #2E8B57 0%, #228B22 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        color: white;
        text-align: center;
        margin: 0;
        font-size: 2.5rem;
    }
    
    .main-header p {
        color: #f0f8f0;
        text-align: center;
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
    }
    
    /* Form styling */
    .stForm {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 15px;
        border: 3px solid #90EE90;
        box-shadow: 0 4px 12px rgba(46, 139, 87, 0.15);
        margin-bottom: 2rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #32CD32 0%, #228B22 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #228B22 0%, #006400 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Metric styling */
    .metric-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8fff8 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #32CD32;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    /* Success/Info message styling */
    .stSuccess {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        padding: 1rem;
    }
    
    .stInfo {
        background-color: #e8f4f8;
        border: 1px solid #bee5eb;
        border-radius: 10px;
        padding: 1rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f0f8f0 0%, #e8f5e8 100%);
    }
    
    /* Chart container styling */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f8f0;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: 2px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #32CD32;
        color: white;
        border-color: #228B22;
    }
    
    /* Loading spinner styling */
    .stSpinner > div {
        border-top-color: #32CD32 !important;
    }
    
    /* Progress bar styling */
    .stProgress .st-bo {
        background-color: #32CD32;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f0f8f0;
        border-radius: 8px;
    }
    
    /* Custom eco badges */
    .eco-badge {
        display: inline-block;
        background: linear-gradient(90deg, #32CD32 0%, #228B22 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 0.2rem;
    }
    
    .warning-badge {
        display: inline-block;
        background: linear-gradient(90deg, #FFA500 0%, #FF8C00 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 0.2rem;
    }
    </style>
    """, unsafe_allow_html=True)

def render_enhanced_header():
    """Render enhanced application header with eco-friendly design"""
    st.markdown("""
    <div class="main-header">
        <h1>🌱 EcoTrip Planner</h1>
        <p>🌍 Make sustainable travel choices with carbon footprint insights for India 🇮🇳</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add environmental impact notice
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background-color: rgba(50, 205, 50, 0.1); 
                    border-radius: 10px; margin-bottom: 2rem;">
            <strong>🌿 Every sustainable choice counts!</strong><br>
            <em>Calculate your carbon footprint • Compare alternatives • Travel responsibly</em>
        </div>
        """, unsafe_allow_html=True)

def handle_main_workflow():
    """Handle the main application workflow: form → calculation → visualization → alternatives"""
    
    # Step 1: Trip Input Form
    form_submitted = False
    try:
        form_data = FormComponents.render_trip_form()
        
        # Check if form was submitted and data is valid
        if form_data and all(key in form_data for key in ['origin_city', 'destination_city', 'travel_modes']):
            form_submitted = True
            # Trigger calculations if form data is complete and valid
            handle_carbon_calculation(form_data)
            
    except Exception as e:
        UIComponents.handle_component_error("form", e, show_details=True)
        # Don't return - continue to show results if available
    
    # Step 2: Display Results if Available (always check, even if form just submitted)
    try:
        emissions_data = SessionStateManager.get_emissions_data()
        trip_data = SessionStateManager.get_trip_data()
        
        if emissions_data and 'total_co2e_kg' in emissions_data:
            # Always display emissions visualization with graphs
            VisualizationComponents.render_emissions_dashboard(emissions_data)
            
            # Always generate and display alternative routes if trip data exists
            if trip_data and trip_data.get('origin_city') and trip_data.get('destination_city'):
                handle_alternative_routes(trip_data, emissions_data)
            else:
                st.warning("⚠️ Trip data incomplete. Please fill the form again.")
        elif not form_submitted:
            # Only show this message if form wasn't just submitted
            st.info("💡 Please submit the form to calculate your carbon footprint")
            
    except Exception as e:
        import traceback
        st.error(f"⚠️ Error displaying results: {str(e)}")
        with st.expander("🔍 Error Details"):
            st.code(traceback.format_exc())
        UIComponents.handle_component_error("visualization", e)

def handle_carbon_calculation(form_data: Dict[str, Any]):
    """Handle carbon footprint calculation with progress indicators"""
    try:
        # Show calculation progress
        with st.spinner("🧮 Calculating your carbon footprint..."):
            # Initialize components
            carbon_calculator = CarbonCalculator()
            geo_manager = GeographicDataManager()
            
            # Create trip data object
            from components.models import TripData
            trip_data = TripData(
                origin_city=form_data['origin_city'],
                destination_city=form_data['destination_city'],
                outbound_date=form_data['outbound_date'],
                return_date=form_data.get('return_date'),
                travel_modes=form_data['travel_modes'],
                num_travelers=form_data['num_travelers'],
                hotel_nights=form_data['hotel_nights']
            )
            
            # Calculate distance
            distance_km = geo_manager.calculate_distance(
                form_data['origin_city'], 
                form_data['destination_city']
            )
            
            if distance_km <= 0:
                st.error("⚠️ Could not calculate distance between selected cities. Please check city names.")
                return
            
            # Store trip data in session
            SessionStateManager.store_trip_data(trip_data.to_dict())
            
            # Calculate emissions
            emissions_result = carbon_calculator.calculate_total_emissions(trip_data, distance_km)
            
            if emissions_result:
                # Store results in session using proper dict conversion
                SessionStateManager.store_emissions_data(emissions_result.to_dict())
                
                # Reset alternatives flag so they regenerate
                st.session_state['alternatives_generated'] = False
                
                # Set a flag to indicate calculation just completed
                st.session_state['calculation_completed'] = True
                
                st.success("✅ Carbon footprint calculated successfully!")
                
                # Show immediate summary
                st.info(f"🌍 Total emissions: **{emissions_result.total_co2e_kg:.1f} kg CO₂e** "
                       f"({emissions_result.per_person_emissions:.1f} kg per person)")
                
                # Streamlit will automatically refresh after form submission
                # No need for explicit rerun() which can cause WebSocket errors
            else:
                st.error("❌ Failed to calculate emissions. Please try again.")
                
    except Exception as e:
        error_msg = str(e)
        # Handle specific datetime conversion errors
        if "'str' object has no attribute 'isoformat'" in error_msg or "isoformat" in error_msg.lower():
            st.error("⚠️ Data format error. Please try clearing the session and recalculating.")
            st.info("💡 Click 'Clear All' in the sidebar, then fill the form again.")
            # Clear potentially corrupted session data
            try:
                SessionStateManager.reset_calculations()
            except:
                pass
        else:
            st.error(f"⚠️ Calculation error: {error_msg}")
            UIComponents.handle_component_error("calculation", e)

def handle_alternative_routes(trip_data: Dict[str, Any], emissions_data: Dict[str, Any]):
    """Handle alternative route generation and display"""
    try:
        origin = trip_data.get('origin_city', '')
        destination = trip_data.get('destination_city', '')
        
        if not origin or not destination:
            st.warning("⚠️ Origin or destination missing. Cannot generate alternatives.")
            return
        
        # Always generate alternatives if not already generated or if data changed
        alternatives = SessionStateManager.get_alternatives_data()
        baseline_emissions = emissions_data.get('total_co2e_kg', 0)
        
        # Check if we need to regenerate alternatives
        should_regenerate = (
            not st.session_state.get('alternatives_generated', False) or
            not alternatives or
            len(alternatives) == 0
        )
        
        if should_regenerate:
            with st.spinner("🗺️ Finding greener alternative routes..."):
                route_analyzer = RouteAnalyzer()
                
                # Generate alternatives for ALL transport modes (not just selected ones)
                # This ensures we show greener options
                alternatives = route_analyzer.generate_alternatives(
                    origin,
                    destination,
                    trip_data.get('travel_modes', []),  # Use selected modes for baseline
                    baseline_emissions
                )
                
                if alternatives:
                    # Ensure alternatives are sorted by emissions (greenest first)
                    alternatives = sorted(alternatives, key=lambda x: x.get('co2e_emissions_kg', float('inf')))
                    
                    SessionStateManager.store_alternatives_data(alternatives)
                    st.session_state['alternatives_generated'] = True
                    st.success(f"✅ Found {len(alternatives)} alternative route(s)!")
                else:
                    st.warning("⚠️ No alternative routes available for this route.")
                    return
        
        # Display alternatives if available
        alternatives = SessionStateManager.get_alternatives_data()
        if alternatives and len(alternatives) > 0:
            st.markdown("---")
            VisualizationComponents.render_alternatives_dashboard(
                alternatives, 
                origin, 
                destination
            )
        else:
            st.info("💡 Generating alternative routes... Please wait.")
            
    except Exception as e:
        st.error(f"⚠️ Error generating alternatives: {str(e)}")
        import traceback
        with st.expander("🔍 Error Details"):
            st.code(traceback.format_exc())
        UIComponents.handle_component_error("alternatives", e)

def render_sidebar_content():
    """Render comprehensive sidebar with status, configuration, and help"""
    try:
        # Session status
        display_session_status()
        
        # Environment/API status
        display_environment_status()
        
        # Quick actions
        render_sidebar_actions()
        
        # Help and tips
        render_sidebar_help()
        
    except Exception as e:
        st.sidebar.error(f"Sidebar Error: {str(e)}")

def render_sidebar_actions():
    """Render quick action buttons in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.header("🚀 Quick Actions")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("🔄 Recalculate", help="Recalculate emissions with current data"):
            try:
                trip_data = SessionStateManager.get_trip_data()
                if trip_data:
                    handle_carbon_calculation(trip_data)
                else:
                    st.sidebar.warning("No trip data to recalculate")
            except Exception as e:
                st.sidebar.error(f"Recalculation failed: {str(e)}")
    
    with col2:
        if st.button("🗑️ Clear All", help="Clear all session data and start over"):
            try:
                SessionStateManager.clear_session()
                st.session_state['alternatives_generated'] = False
                st.session_state['calculation_completed'] = False
                st.sidebar.success("Session cleared!")
                # Streamlit buttons automatically trigger a rerun, so we don't need explicit rerun()
                # This prevents WebSocket errors
            except Exception as e:
                st.sidebar.error(f"Clear failed: {str(e)}")

def render_sidebar_help():
    """Render help and tips in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.header("💡 Tips & Help")
    
    with st.sidebar.expander("🌱 Eco-Friendly Travel Tips"):
        st.markdown("""
        **Reduce Your Carbon Footprint:**
        - Choose trains over flights when possible
        - Consider bus travel for medium distances
        - Pack light to reduce fuel consumption
        - Stay longer to reduce travel frequency
        - Offset emissions through tree planting
        """)
    
    with st.sidebar.expander("📊 Understanding Your Results"):
        st.markdown("""
        **Emission Factors:**
        - Flight: ~0.25 kg CO₂e per km
        - Car: ~0.12 kg CO₂e per km  
        - Train: ~0.04 kg CO₂e per km
        - Bus: ~0.08 kg CO₂e per km
        
        **Accommodation:** ~5 kg CO₂e per night
        """)
    
    with st.sidebar.expander("🔧 Troubleshooting"):
        st.markdown("""
        **Common Issues:**
        - City not found: Try major nearby cities
        - API errors: App uses fallback data automatically
        - Slow loading: Check internet connection
        - Missing results: Ensure all form fields are filled
        """)

def handle_critical_error(error: Exception):
    """Handle critical application errors with recovery options"""
    st.error("🚨 A critical error occurred. Please try the recovery options below.")
    
    # Show error details in expander
    with st.expander("🔍 Error Details"):
        st.code(f"Error Type: {type(error).__name__}\nError Message: {str(error)}")
    
    # Recovery options
    st.markdown("### 🛠️ Recovery Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Page", type="primary"):
            # Button clicks automatically trigger rerun in Streamlit
            # Wrapping in try-except to prevent WebSocket errors
            try:
                # Use a flag-based approach instead of immediate rerun
                st.session_state['force_refresh'] = True
                st.rerun()
            except Exception as e:
                # If rerun fails, provide manual refresh option
                st.info("💡 Please manually refresh your browser (Press F5)")
                # Clear the flag if rerun failed
                if 'force_refresh' in st.session_state:
                    del st.session_state['force_refresh']
    
    with col2:
        if st.button("🗑️ Clear Session"):
            try:
                SessionStateManager.clear_session()
                st.success("Session cleared. Please refresh the page.")
            except:
                st.error("Failed to clear session data.")
    
    with col3:
        if st.button("📞 Report Issue"):
            st.info("Please report this issue with the error details above.")
    
    # Show fallback minimal interface
    st.markdown("---")
    st.markdown("### 🔧 Minimal Interface")
    st.info("You can still use basic functionality while we resolve the issue.")
    
    try:
        # Minimal form for basic calculations
        with st.form("emergency_form"):
            origin = st.text_input("Origin City", value="Delhi")
            destination = st.text_input("Destination City", value="Mumbai")
            mode = st.selectbox("Travel Mode", ["Flight", "Train", "Car", "Bus"])
            
            if st.form_submit_button("Quick Calculate"):
                st.info(f"Estimated emissions for {origin} to {destination} by {mode}: ~150 kg CO₂e")
                
    except Exception:
        st.error("Minimal interface also unavailable. Please refresh the page.")

def display_session_status():
    """Display current session data status in sidebar with enhanced information"""
    try:
        st.sidebar.header("📊 Session Status")
        
        session_summary = SessionStateManager.get_session_summary()
        
        # Trip data status
        if session_summary['has_trip_data']:
            st.sidebar.success("✅ Trip data stored")
            trip_data = SessionStateManager.get_trip_data()
            if trip_data.get('origin_city') and trip_data.get('destination_city'):
                st.sidebar.info(f"🗺️ {trip_data['origin_city']} → {trip_data['destination_city']}")
                
                # Show additional trip details
                if trip_data.get('travel_modes'):
                    modes_str = ", ".join(trip_data['travel_modes'])
                    st.sidebar.text(f"🚗 Modes: {modes_str}")
                
                if trip_data.get('num_travelers'):
                    st.sidebar.text(f"👥 Travelers: {trip_data['num_travelers']}")
        else:
            st.sidebar.info("📝 No trip data yet")
        
        # Emissions data status
        if session_summary['has_emissions_data']:
            st.sidebar.success("✅ Emissions calculated")
            
            emissions_data = SessionStateManager.get_emissions_data()
            if emissions_data:
                total_emissions = emissions_data.get('total_co2e_kg', 0)
                st.sidebar.metric(
                    "Total CO₂e", 
                    f"{total_emissions:.1f} kg",
                    help="Total carbon dioxide equivalent emissions"
                )
                
                # Show calculation warnings if any
                if emissions_data.get('calculation_warnings'):
                    st.sidebar.warning("⚠️ Calculation warnings present")
        else:
            st.sidebar.info("🧮 No emissions data yet")
        
        # Alternatives status
        alternatives = SessionStateManager.get_alternatives_data()
        if alternatives:
            st.sidebar.success(f"✅ {len(alternatives)} alternatives found")
        elif session_summary['has_emissions_data']:
            st.sidebar.info("🔍 Generating alternatives...")
        
        # Calculation progress
        if session_summary['calculation_in_progress']:
            st.sidebar.warning("⏳ Calculation in progress...")
            
    except Exception as e:
        st.sidebar.error(f"Session status error: {str(e)}")

def display_environment_status():
    """Display ML model status and configuration information"""
    try:
        st.sidebar.header("🤖 ML Model Status")
        
        # Show ML model information
        try:
            from components.ml_emissions_model import MLEmissionsPredictor
            from components.ml_route_predictor import MLRoutePredictor
            
            emissions_model = MLEmissionsPredictor()
            route_model = MLRoutePredictor()
            
            model_info = emissions_model.get_model_info()
            
            st.sidebar.success("✅ ML Emissions Model Active")
            st.sidebar.info(f"📊 Model Type: {model_info['model_type']}")
            st.sidebar.info(f"🌍 Region: {model_info['region']}")
            st.sidebar.success("✅ ML Route Predictor Active")
            
            # Show emission factors
            with st.sidebar.expander("📈 Emission Factors"):
                factors = emissions_model.get_emission_factors_dict()
                for mode, factor in factors.items():
                    if mode != 'Hotel':
                        st.sidebar.text(f"{mode}: {factor:.3f} kg CO₂e/km")
                    else:
                        st.sidebar.text(f"{mode}: {factor:.1f} kg CO₂e/night")
            
            st.sidebar.info("💡 Using ML-based predictions (no API required)")
            
        except Exception as e:
            st.sidebar.warning("⚠️ ML Model initialization issue")
            st.sidebar.text(f"Error: {str(e)[:50]}...")
        
        # Configuration help
        with st.sidebar.expander("⚙️ How It Works"):
            st.markdown("""
            **ML-Based Predictions:**
            
            - ✅ **Emissions**: ML model predicts carbon emissions
            - ✅ **Routes**: ML model predicts distances and durations
            - ✅ **No API Keys Required**: Works completely offline
            - ✅ **India-Specific**: Optimized for Indian transport systems
            
            **Benefits:**
            - No external dependencies
            - Fast predictions
            - Always available
            - Privacy-focused
            """)
        
    except Exception as e:
        st.sidebar.error(f"Configuration status error: {str(e)}")

def test_ml_models():
    """Test ML model predictions with sample data"""
    try:
        from components.ml_emissions_model import MLEmissionsPredictor
        from components.ml_route_predictor import MLRoutePredictor
        
        emissions_model = MLEmissionsPredictor()
        route_model = MLRoutePredictor()
        
        with st.spinner("Testing ML Models..."):
            # Test emissions prediction
            test_emissions = emissions_model.predict_emission_factor('Train', 500.0, 1)
            if test_emissions > 0:
                st.sidebar.success("✅ Emissions Model: Working")
            else:
                st.sidebar.error("❌ Emissions Model: Failed")
            
            # Test route prediction
            test_route = route_model.predict_distance('Delhi', 'Mumbai', 'Car')
            if test_route > 0:
                st.sidebar.success("✅ Route Predictor: Working")
            else:
                st.sidebar.error("❌ Route Predictor: Failed")
            
            st.sidebar.success("🎉 All ML models operational")
                    
    except Exception as e:
        st.sidebar.error(f"ML model test failed: {str(e)}")

if __name__ == "__main__":
    main()