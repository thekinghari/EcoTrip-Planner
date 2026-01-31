"""
User interface components for EcoTrip Planner

Contains Streamlit UI components for forms, visualizations, and displays.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
from datetime import date, datetime, timedelta
from .session_manager import SessionStateManager


class UIComponents:
    """Collection of reusable UI components for the application"""
    
    @staticmethod
    def render_header() -> None:
        """Render the main application header"""
        st.title("🌱 EcoTrip Planner")
        st.markdown("**Make sustainable travel choices with carbon footprint insights**")
        st.markdown("---")
    
    @staticmethod
    def render_loading_indicator(message: str = "Calculating...") -> None:
        """Display loading indicator with custom message"""
        return st.spinner(message)
    
    @staticmethod
    def render_calculation_progress(step: str, total_steps: int, current_step: int) -> None:
        """Display calculation progress with step information"""
        progress_percentage = current_step / total_steps
        st.progress(progress_percentage)
        st.text(f"Step {current_step}/{total_steps}: {step}")
    
    @staticmethod
    def render_loading_placeholder() -> None:
        """Display loading placeholder for visualizations"""
        with st.container():
            st.markdown("### 📊 Carbon Footprint Analysis")
            col1, col2 = st.columns([1, 1])
            
            with col1:
                with st.container():
                    st.markdown("#### Emissions Breakdown")
                    st.info("🔄 Calculating emissions breakdown...")
            
            with col2:
                with st.container():
                    st.markdown("#### Benchmark Comparison")
                    st.info("🔄 Preparing benchmark analysis...")
            
            st.markdown("#### 📈 Impact Summary")
            st.info("🔄 Generating impact summary...")
    
    @staticmethod
    def render_error_message(error: str, error_type: str = "general") -> None:
        """Display user-friendly error message with appropriate styling"""
        error_icons = {
            "api": "🌐",
            "network": "📡", 
            "validation": "📝",
            "calculation": "🧮",
            "data": "💾",
            "general": "⚠️"
        }
        
        icon = error_icons.get(error_type, "⚠️")
        st.error(f"{icon} {error}")
    
    @staticmethod
    def render_success_message(message: str) -> None:
        """Display success message"""
        st.success(f"✅ {message}")
    
    @staticmethod
    def render_info_message(message: str) -> None:
        """Display informational message"""
        st.info(f"💡 {message}")
    
    @staticmethod
    def render_warning_message(message: str, warning_type: str = "general") -> None:
        """Display warning message with appropriate styling"""
        warning_icons = {
            "api": "🌐",
            "fallback": "🔄",
            "performance": "⚡",
            "general": "⚠️"
        }
        
        icon = warning_icons.get(warning_type, "⚠️")
        st.warning(f"{icon} {message}")
    
    @staticmethod
    def render_api_status_indicator(api_name: str, is_available: bool, fallback_active: bool = False) -> None:
        """Display API status with fallback information"""
        if is_available and not fallback_active:
            st.success(f"✅ {api_name} API: Connected")
        elif fallback_active:
            st.warning(f"🔄 {api_name} API: Using fallback data")
        else:
            st.error(f"❌ {api_name} API: Unavailable")
    
    @staticmethod
    def render_network_error_help() -> None:
        """Display helpful information for network errors"""
        with st.expander("🔧 Troubleshooting Network Issues"):
            st.markdown("""
            **If you're experiencing connection issues:**
            
            1. **Check your internet connection**
               - Ensure you have a stable internet connection
               - Try refreshing the page
            
            2. **API Service Status**
               - External services may be temporarily unavailable
               - The app will automatically use fallback data when possible
            
            3. **Firewall/Proxy Issues**
               - Corporate networks may block certain API calls
               - Contact your IT administrator if needed
            
            4. **Temporary Service Outage**
               - External APIs may experience temporary downtime
               - Try again in a few minutes
            
            **Note:** The app continues to work with static data when APIs are unavailable.
            """)
    
    @staticmethod
    def render_validation_error_help(errors: List[str]) -> None:
        """Display helpful information for validation errors"""
        st.error("📝 Please fix the following issues:")
        for error in errors:
            st.markdown(f"• {error}")
        
        with st.expander("💡 Input Guidelines"):
            st.markdown("""
            **Form Completion Tips:**
            
            - **Cities**: Enter valid Indian city names (e.g., Mumbai, Delhi, Chennai)
            - **Dates**: Select future dates, return date must be after departure
            - **Travel Modes**: Choose at least one transportation method
            - **Travelers**: Must be between 1 and 20 people
            - **Hotel Nights**: Enter 0 for day trips, maximum 365 nights
            
            **Popular Routes Available:**
            Use the dropdown to quickly select common Indian routes like Delhi-Mumbai or Chennai-Bangalore.
            """)
    
    @staticmethod
    def handle_component_error(component_name: str, error: Exception, show_details: bool = False) -> None:
        """Handle component-level errors with user-friendly messages"""
        error_messages = {
            "form": "There was an issue with the form. Please try refreshing the page.",
            "visualization": "Unable to display charts. Your data is still saved.",
            "map": "Map display is unavailable. Route information is still accessible.",
            "calculation": "Calculation service is temporarily unavailable. Using fallback estimates.",
            "api": "External service is temporarily unavailable. Using cached data.",
            "session": "Session data issue detected. Your progress has been preserved."
        }
        
        user_message = error_messages.get(component_name, "An unexpected error occurred. Please try again.")
        UIComponents.render_error_message(user_message, "general")
        
        if show_details:
            with st.expander("🔍 Technical Details"):
                st.code(f"Component: {component_name}\nError: {str(error)}")
        
        # Log error for debugging (in a real app, this would go to a logging service)
        st.sidebar.error(f"Debug: {component_name} error - {type(error).__name__}")
    
    @staticmethod
    def render_fallback_notice(service_name: str, fallback_type: str) -> None:
        """Display notice when fallback mechanisms are active"""
        fallback_messages = {
            "static_data": f"Using reliable static data for {service_name}",
            "cached_data": f"Using previously cached data for {service_name}",
            "estimation": f"Using estimation algorithms for {service_name}",
            "default_values": f"Using default values for {service_name}"
        }
        
        message = fallback_messages.get(fallback_type, f"Using alternative method for {service_name}")
        UIComponents.render_warning_message(f"Fallback Active: {message}", "fallback")
    
    @staticmethod
    def render_sidebar_status() -> None:
        """Render configuration status in sidebar"""
        st.sidebar.header("🔧 Configuration Status")
        # Placeholder for API status checks
        st.sidebar.info("API configuration will be displayed here")


class FormComponents:
    """Components specifically for form rendering and validation"""
    
    # Popular Indian routes for auto-population
    POPULAR_ROUTES = {
        "Salem to Chennai": ("Salem", "Chennai"),
        "Delhi to Mumbai": ("Delhi", "Mumbai"),
        "Bangalore to Hyderabad": ("Bangalore", "Hyderabad"),
        "Chennai to Bangalore": ("Chennai", "Bangalore"),
        "Mumbai to Pune": ("Mumbai", "Pune"),
        "Delhi to Jaipur": ("Delhi", "Jaipur"),
        "Kolkata to Bhubaneswar": ("Kolkata", "Bhubaneswar"),
        "Kochi to Thiruvananthapuram": ("Kochi", "Thiruvananthapuram"),
        "Ahmedabad to Surat": ("Ahmedabad", "Surat"),
        "Goa to Mumbai": ("Goa", "Mumbai")
    }
    
    # Available travel modes
    TRAVEL_MODES = ["Flight", "Train", "Car", "Bus"]
    
    @staticmethod
    def render_trip_form() -> Dict[str, Any]:
        """Render the main trip input form with validation and auto-population"""
        st.subheader("📝 Trip Details")
        
        # Initialize form data from session state or defaults
        existing_data = SessionStateManager.get_trip_data()
        
        with st.form("trip_input_form"):
            # Popular routes dropdown for auto-population
            st.markdown("**Quick Select Popular Routes** 🚀")
            selected_route = st.selectbox(
                "Choose a popular route (optional)",
                options=["Select a route..."] + list(FormComponents.POPULAR_ROUTES.keys()),
                help="Select a popular route to auto-fill origin and destination"
            )
            
            # Origin and destination with default values
            col1, col2 = st.columns(2)
            
            with col1:
                # Auto-populate from selected route or use existing/default
                default_origin = "Salem"
                if selected_route != "Select a route..." and selected_route in FormComponents.POPULAR_ROUTES:
                    default_origin = FormComponents.POPULAR_ROUTES[selected_route][0]
                elif existing_data.get('origin_city'):
                    default_origin = existing_data['origin_city']
                
                origin_city = st.text_input(
                    "Origin City *",
                    value=default_origin,
                    help="Enter your departure city"
                )
            
            with col2:
                # Auto-populate from selected route or use existing/default
                default_destination = "Chennai"
                if selected_route != "Select a route..." and selected_route in FormComponents.POPULAR_ROUTES:
                    default_destination = FormComponents.POPULAR_ROUTES[selected_route][1]
                elif existing_data.get('destination_city'):
                    default_destination = existing_data['destination_city']
                
                destination_city = st.text_input(
                    "Destination City *",
                    value=default_destination,
                    help="Enter your arrival city"
                )
            
            # Travel dates
            st.markdown("**Travel Dates** 📅")
            col3, col4 = st.columns(2)
            
            with col3:
                # Default to tomorrow if no existing data
                default_outbound = existing_data.get('outbound_date')
                if default_outbound and isinstance(default_outbound, str):
                    default_outbound = date.fromisoformat(default_outbound)
                elif not default_outbound:
                    default_outbound = date.today() + timedelta(days=1)
                
                outbound_date = st.date_input(
                    "Outbound Date *",
                    value=default_outbound,
                    min_value=date.today(),
                    help="Select your departure date"
                )
            
            with col4:
                # Return date is optional
                default_return = existing_data.get('return_date')
                if default_return and isinstance(default_return, str):
                    default_return = date.fromisoformat(default_return)
                
                return_date = st.date_input(
                    "Return Date (optional)",
                    value=default_return,
                    min_value=outbound_date + timedelta(days=1) if outbound_date else date.today() + timedelta(days=2),
                    help="Select your return date (leave empty for one-way trip)"
                )
            
            # Travel modes (multiselect)
            st.markdown("**Travel Modes** 🚗")
            default_modes = existing_data.get('travel_modes', ["Flight"])
            travel_modes = st.multiselect(
                "Select travel modes *",
                options=FormComponents.TRAVEL_MODES,
                default=default_modes,
                help="Choose one or more transportation methods"
            )
            
            # Number of travelers and hotel nights
            col5, col6 = st.columns(2)
            
            with col5:
                num_travelers = st.number_input(
                    "Number of Travelers *",
                    min_value=1,
                    max_value=20,
                    value=existing_data.get('num_travelers', 1),
                    help="Total number of people traveling"
                )
            
            with col6:
                hotel_nights = st.number_input(
                    "Hotel Nights",
                    min_value=0,
                    max_value=365,
                    value=existing_data.get('hotel_nights', 0),
                    help="Number of nights staying in hotels"
                )
            
            # Form submission
            submitted = st.form_submit_button("Calculate Carbon Footprint 🌱", type="primary")
            
            if submitted:
                # Prepare form data
                form_data = {
                    'origin_city': origin_city.strip(),
                    'destination_city': destination_city.strip(),
                    'outbound_date': outbound_date.isoformat(),
                    'return_date': return_date.isoformat() if return_date else None,
                    'travel_modes': travel_modes,
                    'num_travelers': int(num_travelers),
                    'hotel_nights': int(hotel_nights)
                }
                
                # Validate form data with enhanced error handling
                try:
                    validation_result = FormComponents.validate_form_data(form_data)
                    
                    if validation_result['is_valid']:
                        # Store valid data in session state
                        try:
                            SessionStateManager.store_trip_data(form_data)
                            st.success("✅ Trip data saved successfully!")
                            
                            # Display warnings if any
                            if validation_result.get('warnings'):
                                for warning in validation_result['warnings']:
                                    st.warning(f"💡 {warning}")
                            
                            return form_data
                        except Exception as e:
                            UIComponents.render_error_message(
                                "Failed to save trip data. Please try again.", 
                                "data"
                            )
                            st.sidebar.error(f"Session Error: {str(e)}")
                            return {}
                    else:
                        # Display validation errors with helpful guidance
                        UIComponents.render_validation_error_help(validation_result['errors'])
                        
                        # Display warnings if any
                        if validation_result.get('warnings'):
                            for warning in validation_result['warnings']:
                                st.warning(f"💡 {warning}")
                        
                        return {}
                        
                except Exception as e:
                    UIComponents.render_error_message(
                        "Form validation failed. Please check your inputs and try again.", 
                        "validation"
                    )
                    st.sidebar.error(f"Validation Error: {str(e)}")
                    return {}
            
            # Return current form state even if not submitted
            return {
                'origin_city': origin_city.strip(),
                'destination_city': destination_city.strip(),
                'outbound_date': outbound_date.isoformat(),
                'return_date': return_date.isoformat() if return_date else None,
                'travel_modes': travel_modes,
                'num_travelers': int(num_travelers),
                'hotel_nights': int(hotel_nights)
            }
    
    @staticmethod
    def validate_form_data(form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate form data integrity and return validation result with detailed error handling"""
        errors = []
        warnings = []
        
        try:
            # Check required fields (strip whitespace for validation)
            origin_city = form_data.get('origin_city', '')
            if origin_city is None:
                origin_city = ''
            elif isinstance(origin_city, str):
                origin_city = origin_city.strip()
            else:
                origin_city = str(origin_city).strip()
                
            if not origin_city:
                errors.append("Origin city is required")
            elif len(origin_city) < 2:
                errors.append("Origin city name must be at least 2 characters")
            elif len(origin_city) > 50:
                errors.append("Origin city name cannot exceed 50 characters")
            
            destination_city = form_data.get('destination_city', '')
            if destination_city is None:
                destination_city = ''
            elif isinstance(destination_city, str):
                destination_city = destination_city.strip()
            else:
                destination_city = str(destination_city).strip()
                
            if not destination_city:
                errors.append("Destination city is required")
            elif len(destination_city) < 2:
                errors.append("Destination city name must be at least 2 characters")
            elif len(destination_city) > 50:
                errors.append("Destination city name cannot exceed 50 characters")
            
            if not form_data.get('outbound_date'):
                errors.append("Outbound date is required")
            
            if not form_data.get('travel_modes'):
                errors.append("At least one travel mode must be selected")
            
            # Validate numeric inputs with detailed error messages
            try:
                num_travelers = form_data.get('num_travelers', 0)
                if not isinstance(num_travelers, (int, float)):
                    errors.append("Number of travelers must be a valid number")
                elif num_travelers < 1:
                    errors.append("Number of travelers must be at least 1")
                elif num_travelers > 20:
                    errors.append("Number of travelers cannot exceed 20 (for group bookings, please contact travel agents)")
                elif num_travelers != int(num_travelers):
                    errors.append("Number of travelers must be a whole number")
            except (ValueError, TypeError):
                errors.append("Number of travelers must be a valid number")
            
            try:
                hotel_nights = form_data.get('hotel_nights', 0)
                if not isinstance(hotel_nights, (int, float)):
                    errors.append("Hotel nights must be a valid number")
                elif hotel_nights < 0:
                    errors.append("Hotel nights cannot be negative")
                elif hotel_nights > 365:
                    errors.append("Hotel nights cannot exceed 365 (for extended stays, please split into multiple trips)")
                elif hotel_nights != int(hotel_nights):
                    errors.append("Hotel nights must be a whole number")
            except (ValueError, TypeError):
                errors.append("Hotel nights must be a valid number")
            
            # Validate travel modes with specific error messages
            valid_modes = set(FormComponents.TRAVEL_MODES)
            selected_modes = form_data.get('travel_modes')
            
            if selected_modes is None:
                selected_modes = []
            elif not isinstance(selected_modes, list):
                selected_modes = []
                
            if not selected_modes:
                errors.append("At least one travel mode must be selected")
            else:
                invalid_modes = [mode for mode in selected_modes if mode not in valid_modes]
                if invalid_modes:
                    errors.append(f"Invalid travel mode(s) selected: {', '.join(invalid_modes)}")
                
                # Check for logical combinations
                if len(selected_modes) > 3:
                    warnings.append("Multiple travel modes selected - this may result in complex route calculations")
            
            # Validate dates with comprehensive error handling
            try:
                from datetime import date, timedelta
                
                outbound_date_str = form_data.get('outbound_date')
                if not outbound_date_str or outbound_date_str is None:
                    errors.append("Outbound date is required")
                else:
                    try:
                        outbound_date = date.fromisoformat(str(outbound_date_str))
                        today = date.today()
                        
                        if outbound_date < today:
                            errors.append("Outbound date cannot be in the past")
                        elif outbound_date > today + timedelta(days=365):
                            warnings.append("Outbound date is more than a year in the future - emission factors may change")
                        
                        return_date_str = form_data.get('return_date')
                        if return_date_str and return_date_str is not None:
                            try:
                                return_date = date.fromisoformat(str(return_date_str))
                                if return_date <= outbound_date:
                                    errors.append("Return date must be after outbound date")
                                elif (return_date - outbound_date).days > 365:
                                    warnings.append("Trip duration exceeds one year - consider splitting into multiple trips")
                                elif (return_date - outbound_date).days == 0:
                                    errors.append("Same-day return trips are not supported - use one-way trip instead")
                            except (ValueError, TypeError):
                                errors.append("Return date format is invalid - please select a valid date")
                                
                    except (ValueError, TypeError):
                        errors.append("Outbound date format is invalid - please select a valid date")
                        
            except Exception:
                errors.append("Date validation failed - please check your date selections")
            
            # Check if origin and destination are the same (after stripping whitespace)
            # Allow same origin/destination only for accommodation-only trips (no travel modes)
            if (origin_city and destination_city and 
                origin_city.lower() == destination_city.lower() and
                selected_modes):  # Only reject if there are travel modes
                errors.append("Origin and destination cities cannot be the same")
            
            # Additional validation for city names (basic format checking)
            if origin_city and len(origin_city) > 0:
                if not origin_city.replace(' ', '').replace('-', '').isalpha():
                    warnings.append("Origin city name contains unusual characters - please verify spelling")
            
            if destination_city and len(destination_city) > 0:
                if not destination_city.replace(' ', '').replace('-', '').isalpha():
                    warnings.append("Destination city name contains unusual characters - please verify spelling")
            
            # Validate logical combinations
            if (form_data.get('hotel_nights', 0) == 0 and 
                form_data.get('return_date') and 
                form_data.get('outbound_date')):
                try:
                    outbound = date.fromisoformat(form_data['outbound_date'])
                    return_dt = date.fromisoformat(form_data['return_date'])
                    if (return_dt - outbound).days > 0:
                        warnings.append("Multi-day trip with no hotel nights - consider adding accommodation")
                except:
                    pass  # Date parsing already handled above
            
        except Exception as e:
            # Catch any unexpected validation errors and provide user-friendly message
            errors.append("Form validation encountered an issue - please check all fields and try again")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def handle_form_submission_error(error: Exception) -> None:
        """Handle form submission errors with user-friendly messages"""
        from components.ui_components import UIComponents
        
        error_type = type(error).__name__
        
        if "ValidationError" in error_type or "ValueError" in error_type:
            UIComponents.render_error_message(
                "Please check your input data and try again.", 
                "validation"
            )
        elif "ConnectionError" in error_type or "TimeoutError" in error_type:
            UIComponents.render_error_message(
                "Network connection issue. Please check your internet connection and try again.", 
                "network"
            )
        elif "SessionError" in error_type:
            UIComponents.render_error_message(
                "Session data issue. Please refresh the page and try again.", 
                "data"
            )
        else:
            UIComponents.render_error_message(
                "An unexpected error occurred. Please try again or refresh the page.", 
                "general"
            )
        
        # Show technical details in sidebar for debugging
        st.sidebar.error(f"Form Error: {error_type} - {str(error)}")
    
    @staticmethod
    def render_trip_form_with_error_handling() -> Dict[str, Any]:
        """Enhanced trip form with comprehensive error handling"""
        try:
            return FormComponents.render_trip_form()
        except Exception as e:
            FormComponents.handle_form_submission_error(e)
            return {}
    
    @staticmethod
    def populate_popular_routes(route_key: str) -> Dict[str, str]:
        """Auto-populate origin and destination from popular routes selection"""
        if route_key in FormComponents.POPULAR_ROUTES:
            origin, destination = FormComponents.POPULAR_ROUTES[route_key]
            return {
                'origin_city': origin,
                'destination_city': destination
            }
        return {}


class VisualizationComponents:
    """Components for data visualization and charts"""
    
    # Benchmark data for Indian domestic trips (kg CO2e per person)
    INDIAN_TRIP_BENCHMARKS = {
        'Short Distance (< 500km)': 45.0,
        'Medium Distance (500-1500km)': 120.0,
        'Long Distance (> 1500km)': 280.0,
        'Average Domestic Trip': 150.0
    }
    
    @staticmethod
    def render_emissions_dashboard(emissions_data: Dict[str, Any]) -> None:
        """Render comprehensive emissions visualization dashboard with real-time updates"""
        try:
            # Check if calculation is in progress
            if SessionStateManager.is_calculation_in_progress():
                UIComponents.render_loading_placeholder()
                return
            
            if not emissions_data or 'total_co2e_kg' not in emissions_data:
                st.info("💡 Complete the trip form above to see your carbon footprint analysis")
                return
            
            st.subheader("📊 Carbon Footprint Analysis")
            
            # Create columns for layout
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Pie chart for emissions breakdown
                try:
                    VisualizationComponents._render_emissions_pie_chart(emissions_data)
                except Exception as e:
                    st.error(f"Error rendering pie chart: {str(e)}")
                    st.info("Showing data summary instead...")
                    transport_total = sum(emissions_data.get('transport_emissions', {}).values())
                    accommodation_total = emissions_data.get('accommodation_emissions', 0.0)
                    st.write(f"Transport: {transport_total:.1f} kg CO₂e")
                    st.write(f"Accommodation: {accommodation_total:.1f} kg CO₂e")
            
            with col2:
                # Bar chart for benchmark comparisons
                try:
                    VisualizationComponents._render_benchmark_comparison(emissions_data)
                except Exception as e:
                    st.error(f"Error rendering benchmark chart: {str(e)}")
                    per_person = emissions_data.get('per_person_emissions', 0.0)
                    st.metric("Per Person Emissions", f"{per_person:.1f} kg CO₂e")
            
            # Textual summary below charts
            try:
                VisualizationComponents._render_impact_summary(emissions_data)
            except Exception as e:
                st.warning(f"Error rendering impact summary: {str(e)}")
            
            # Additional visualizations
            st.markdown("---")
            try:
                VisualizationComponents._render_transport_mode_comparison(emissions_data)
            except Exception as e:
                st.warning(f"Error rendering transport mode comparison: {str(e)}")
            
            # Add refresh indicator if data is fresh (calculated within last 5 minutes)
            if 'calculation_timestamp' in emissions_data:
                try:
                    if isinstance(emissions_data['calculation_timestamp'], str):
                        calc_time = datetime.fromisoformat(emissions_data['calculation_timestamp'])
                    else:
                        calc_time = emissions_data['calculation_timestamp']
                    time_diff = datetime.now() - calc_time
                    if time_diff.total_seconds() < 300:  # 5 minutes
                        st.success("✅ Results updated successfully!")
                except (ValueError, TypeError):
                    pass  # Ignore timestamp parsing errors
        except Exception as e:
            st.error(f"Error displaying emissions dashboard: {str(e)}")
            # Show basic data even if visualization fails
            if emissions_data:
                st.write("**Basic Emissions Data:**")
                st.write(f"Total: {emissions_data.get('total_co2e_kg', 0):.1f} kg CO₂e")
                st.write(f"Per Person: {emissions_data.get('per_person_emissions', 0):.1f} kg CO₂e")
    
    @staticmethod
    def _render_emissions_pie_chart(emissions_data: Dict[str, Any]) -> None:
        """Create pie chart showing breakdown between transport and accommodation emissions"""
        # Calculate transport total from individual modes
        transport_emissions = emissions_data.get('transport_emissions', {})
        transport_total = sum(transport_emissions.values())
        accommodation_total = emissions_data.get('accommodation_emissions', 0.0)
        
        # Prepare data for pie chart
        if transport_total > 0 or accommodation_total > 0:
            labels = []
            values = []
            colors = []
            
            if transport_total > 0:
                labels.append('Transportation')
                values.append(transport_total)
                colors.append('#2E8B57')  # Sea green for transport
            
            if accommodation_total > 0:
                labels.append('Accommodation')
                values.append(accommodation_total)
                colors.append('#FF6B6B')  # Coral for accommodation
            
            # Create pie chart
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.4,  # Donut chart style
                marker_colors=colors,
                textinfo='label+percent+value',
                texttemplate='%{label}<br>%{percent}<br>%{value:.1f} kg CO₂e',
                hovertemplate='<b>%{label}</b><br>%{value:.2f} kg CO₂e<br>%{percent}<extra></extra>'
            )])
            
            fig.update_layout(
                title={
                    'text': 'Emissions Breakdown',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 16, 'color': '#2F4F4F'}
                },
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5,
                    font={'size': 12}
                ),
                margin=dict(t=50, b=50, l=20, r=20),
                height=350,
                autosize=True
            )
            
            # Use config for responsive charts
            config = {'displayModeBar': True, 'responsive': True, 'displaylogo': False}
            st.plotly_chart(fig, use_container_width=True, config=config)
        else:
            st.info("No emissions data available for breakdown")
    
    @staticmethod
    def _render_benchmark_comparison(emissions_data: Dict[str, Any]) -> None:
        """Create bar chart comparing trip emissions against Indian domestic trip benchmarks"""
        per_person_emissions = emissions_data.get('per_person_emissions', 0.0)
        
        if per_person_emissions <= 0:
            st.info("No per-person emissions data available for comparison")
            return
        
        # Prepare benchmark comparison data
        benchmarks = VisualizationComponents.INDIAN_TRIP_BENCHMARKS.copy()
        benchmarks['Your Trip'] = per_person_emissions
        
        # Create bar chart
        categories = list(benchmarks.keys())
        values = list(benchmarks.values())
        
        # Create shorter category names for better mobile display
        short_categories = []
        for cat in categories:
            if cat == 'Short Distance (< 500km)':
                short_categories.append('Short')
            elif cat == 'Medium Distance (500-1500km)':
                short_categories.append('Medium')
            elif cat == 'Long Distance (> 1500km)':
                short_categories.append('Long')
            elif cat == 'Average Domestic Trip':
                short_categories.append('Average')
            else:
                short_categories.append('Your Trip')
        
        # Color coding: green for lower emissions, red for higher
        colors = []
        for category in categories:
            if category == 'Your Trip':
                colors.append('#1f77b4')  # Blue for user's trip
            elif benchmarks[category] <= per_person_emissions:
                colors.append('#90EE90')  # Light green for lower benchmarks
            else:
                colors.append('#FFB6C1')  # Light pink for higher benchmarks
        
        fig = go.Figure(data=[go.Bar(
            x=short_categories,
            y=values,
            marker_color=colors,
            text=[f'{v:.1f}' for v in values],
            textposition='auto',
            hovertemplate='<b>%{customdata}</b><br>%{y:.2f} kg CO₂e per person<extra></extra>',
            customdata=categories  # Use full names in hover
        )])
        
        fig.update_layout(
            title={
                'text': 'Benchmark Comparison',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#2F4F4F'}
            },
            xaxis_title='Trip Category',
            yaxis_title='CO₂e Emissions (kg)',
            xaxis={
                'tickangle': 0,  # Keep horizontal to prevent overlap
                'tickfont': {'size': 11},
                'tickmode': 'array',
                'tickvals': list(range(len(short_categories))),
                'ticktext': short_categories
            },
            yaxis={'tickfont': {'size': 11}},
            margin=dict(t=40, b=80, l=50, r=20),  # Reduced top margin to prevent title overlap
            height=350,
            autosize=True
        )
        
        # Use config for responsive charts with minimal toolbar to prevent title overlap
        config = {
            'displayModeBar': True, 
            'responsive': True, 
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d', 'autoScale2d', 'toggleHover', 'toggleSpikelines'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'benchmark_comparison',
                'height': 350,
                'width': 700,
                'scale': 1
            }
        }
        st.plotly_chart(fig, use_container_width=True, config=config)
        
        # Add a legend below the chart to explain the shortened names
        st.markdown("""
        <div style="font-size: 0.85rem; color: #666; text-align: center; margin-top: -15px; margin-bottom: 10px;">
        <strong>Per Person Emissions:</strong> Short (&lt;500km) • Medium (500-1500km) • Long (&gt;1500km) • Average (Indian domestic) • Your Trip
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _render_transport_mode_comparison(emissions_data: Dict[str, Any]) -> None:
        """Create bar chart comparing emissions by transport mode"""
        transport_emissions = emissions_data.get('transport_emissions', {})
        
        if not transport_emissions:
            return
        
        st.subheader("🚗 Transport Mode Comparison")
        
        modes = list(transport_emissions.keys())
        emissions = list(transport_emissions.values())
        
        # Color coding: green for lower emissions, red for higher
        colors = ['#2E8B57' if e < sum(emissions) / len(emissions) else '#FF6B6B' for e in emissions]
        
        fig = go.Figure(data=[go.Bar(
            x=modes,
            y=emissions,
            marker_color=colors,
            text=[f'{e:.1f} kg' for e in emissions],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>%{y:.2f} kg CO₂e<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': 'Emissions by Transport Mode',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#2F4F4F'}
            },
            xaxis_title='Transport Mode',
            yaxis_title='CO₂e Emissions (kg)',
            xaxis={'tickfont': {'size': 11}},
            yaxis={'tickfont': {'size': 11}},
            margin=dict(t=50, b=50, l=50, r=20),
            height=350,
            autosize=True
        )
        
        # Use config for responsive charts
        config = {'displayModeBar': True, 'responsive': True, 'displaylogo': False}
        st.plotly_chart(fig, use_container_width=True, config=config)
    
    @staticmethod
    def _render_impact_summary(emissions_data: Dict[str, Any]) -> None:
        """Display textual summary with emission values and percentages"""
        total_emissions = emissions_data.get('total_co2e_kg', 0.0)
        per_person_emissions = emissions_data.get('per_person_emissions', 0.0)
        transport_emissions = emissions_data.get('transport_emissions', {})
        accommodation_emissions = emissions_data.get('accommodation_emissions', 0.0)
        
        # Calculate percentages
        transport_total = sum(transport_emissions.values())
        if total_emissions > 0:
            transport_percentage = (transport_total / total_emissions) * 100
            accommodation_percentage = (accommodation_emissions / total_emissions) * 100
        else:
            transport_percentage = 0
            accommodation_percentage = 0
        
        # Create summary section
        st.markdown("### 📈 Impact Summary")
        
        # Main metrics in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Emissions",
                value=f"{total_emissions:.1f} kg CO₂e",
                help="Total carbon dioxide equivalent emissions for your entire trip"
            )
        
        with col2:
            st.metric(
                label="Per Person",
                value=f"{per_person_emissions:.1f} kg CO₂e",
                help="Carbon emissions per traveler"
            )
        
        with col3:
            # Compare against average benchmark
            avg_benchmark = VisualizationComponents.INDIAN_TRIP_BENCHMARKS['Average Domestic Trip']
            difference = per_person_emissions - avg_benchmark
            
            # Show savings (positive when user is better than average)
            if difference <= 0:
                # User is better than or equal to average - show as positive savings
                savings = abs(difference)
                delta_color = "normal"  # Green for good performance
                value_text = f"+{savings:.1f} kg saved"
                delta_text = f"{abs((difference/avg_benchmark)*100):.1f}% better"
            else:
                # User is worse than average - show as excess emissions
                excess = difference
                delta_color = "inverse"  # Red for poor performance
                value_text = f"+{excess:.1f} kg more"
                delta_text = f"{(difference/avg_benchmark)*100:.1f}% higher"
            
            st.metric(
                label="vs Average Trip",
                value=value_text,
                delta=delta_text,
                delta_color=delta_color,
                help="Comparison with average Indian domestic trip emissions"
            )
        
        # Detailed breakdown
        st.markdown("#### Emissions Breakdown")
        
        breakdown_text = []
        if transport_total > 0:
            breakdown_text.append(f"🚗 **Transportation**: {transport_total:.1f} kg CO₂e ({transport_percentage:.1f}%)")
            
            # Show breakdown by transport mode if multiple modes
            if len(transport_emissions) > 1:
                for mode, emissions in transport_emissions.items():
                    mode_percentage = (emissions / total_emissions) * 100 if total_emissions > 0 else 0
                    breakdown_text.append(f"   • {mode}: {emissions:.1f} kg CO₂e ({mode_percentage:.1f}%)")
        
        if accommodation_emissions > 0:
            breakdown_text.append(f"🏨 **Accommodation**: {accommodation_emissions:.1f} kg CO₂e ({accommodation_percentage:.1f}%)")
        
        if breakdown_text:
            for text in breakdown_text:
                st.markdown(text)
        else:
            st.info("No emissions breakdown available")
        
        # Environmental context
        st.markdown("#### 🌍 Environmental Context")
        
        # Calculate equivalent comparisons
        tree_months = total_emissions / 21.77  # Average tree absorbs ~21.77 kg CO2 per year
        car_km = total_emissions / 0.12  # Average car emits ~0.12 kg CO2 per km
        
        context_col1, context_col2 = st.columns(2)
        
        with context_col1:
            st.info(f"🌳 Equivalent to **{tree_months:.1f} months** of CO₂ absorption by one tree")
        
        with context_col2:
            st.info(f"🚗 Equivalent to driving **{car_km:.0f} km** in an average car")
    
    @staticmethod
    def render_alternatives_table(alternatives: List[Dict[str, Any]]) -> None:
        """Create structured table showing alternatives with all required columns"""
        if not alternatives:
            st.info("💡 No alternative routes available. Complete the trip form to see route suggestions.")
            return
        
        st.subheader("🌱 Greener Alternative Routes & Recommendations")
        
        # Sort alternatives by emissions (greenest first)
        alternatives_sorted = sorted(alternatives, key=lambda x: x.get('co2e_emissions_kg', float('inf')))
        
        # Highlight greenest options
        if alternatives_sorted:
            greenest = alternatives_sorted[0]
            st.success(f"🌿 **Greenest Option**: {greenest.get('transport_mode', 'Unknown')} with {greenest.get('co2e_emissions_kg', 0):.1f} kg CO₂e emissions")
        
        st.markdown("---")
        
        # Create table data
        table_data = []
        for alt in alternatives_sorted:
            # Format emissions savings with color coding
            savings_kg = alt.get('emissions_savings_kg', 0.0)
            if savings_kg > 0:
                savings_text = f"✅ +{savings_kg:.1f} kg saved"
                savings_color = "green"
            elif savings_kg < 0:
                savings_text = f"❌ +{abs(savings_kg):.1f} kg more"
                savings_color = "red"
            else:
                savings_text = "➖ 0.0 kg"
                savings_color = "gray"
            
            # Format cost difference
            cost_diff = alt.get('cost_difference_inr', 0.0)
            if cost_diff > 0:
                cost_text = f"💰 +₹{cost_diff:.0f} more"
            elif cost_diff < 0:
                cost_text = f"💚 ₹{abs(cost_diff):.0f} saved"
            else:
                cost_text = "➖ ₹0"
            
            table_data.append({
                'Mode': f"{alt.get('transport_mode', 'Unknown')} {VisualizationComponents._get_mode_emoji(alt.get('transport_mode', ''))}",
                'Duration': f"{alt.get('duration_hours', 0):.1f} hrs",
                'Distance': f"{alt.get('distance_km', 0):.0f} km",
                'Emissions': f"{alt.get('co2e_emissions_kg', 0):.1f} kg CO₂e",
                'Savings': savings_text,
                'Cost': f"₹{alt.get('estimated_cost_inr', 0):.0f}",
                'Cost Diff': cost_text
            })
        
        # Display table
        if table_data:
            import pandas as pd
            df = pd.DataFrame(table_data)
            st.dataframe(df, width='stretch', hide_index=True)
            
            # Add summary statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                best_emissions = alternatives_sorted[0] if alternatives_sorted else {}
                savings_value = best_emissions.get('emissions_savings_kg', 0)
                emissions_value = best_emissions.get('co2e_emissions_kg', 0)
                mode_name = best_emissions.get('transport_mode', 'Unknown')
                st.metric(
                    label="🌱 Greenest Option",
                    value=f"{mode_name}",
                    delta=f"{emissions_value:.1f} kg CO₂e" if emissions_value > 0 else None,
                    delta_color="inverse"
                )
                # Show savings separately if available
                if savings_value > 0:
                    st.caption(f"💚 Saves {savings_value:.1f} kg vs baseline")
            
            with col2:
                best_cost = min(alternatives_sorted, key=lambda x: x.get('estimated_cost_inr', float('inf')))
                st.metric(
                    label="💰 Cheapest Option",
                    value=f"{best_cost.get('transport_mode', 'Unknown')}",
                    delta=f"₹{best_cost.get('estimated_cost_inr', 0):.0f}"
                )
            
            with col3:
                fastest = min(alternatives_sorted, key=lambda x: x.get('duration_hours', float('inf')))
                st.metric(
                    label="⚡ Fastest Option",
                    value=f"{fastest.get('transport_mode', 'Unknown')}",
                    delta=f"{fastest.get('duration_hours', 0):.1f} hrs"
                )
        
        # Add emissions comparison chart for alternatives
        VisualizationComponents._render_alternatives_emissions_chart(alternatives_sorted)
    
    @staticmethod
    def _render_alternatives_emissions_chart(alternatives: List[Dict[str, Any]]) -> None:
        """Create bar chart comparing emissions of alternative routes"""
        if not alternatives:
            return
        
        st.markdown("---")
        st.subheader("📊 Emissions Comparison: Alternative Routes")
        
        modes = [alt.get('transport_mode', 'Unknown') for alt in alternatives]
        emissions = [alt.get('co2e_emissions_kg', 0) for alt in alternatives]
        savings = [alt.get('emissions_savings_kg', 0) for alt in alternatives]
        
        # Color coding: green for positive savings, red for negative
        colors = ['#2E8B57' if s > 0 else '#FF6B6B' if s < 0 else '#808080' for s in savings]
        
        fig = go.Figure()
        
        # Add emissions bars
        fig.add_trace(go.Bar(
            x=modes,
            y=emissions,
            name='Emissions',
            marker_color=colors,
            text=[f'{e:.1f} kg' for e in emissions],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Emissions: %{y:.2f} kg CO₂e<br>Savings: %{customdata:.1f} kg<extra></extra>',
            customdata=savings
        ))
        
        fig.update_layout(
            title={
                'text': 'CO₂e Emissions by Alternative Route',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 16, 'color': '#2F4F4F'}
            },
            xaxis_title='Transport Mode',
            yaxis_title='CO₂e Emissions (kg)',
            xaxis={'tickfont': {'size': 11}},
            yaxis={'tickfont': {'size': 11}},
            showlegend=False,
            margin=dict(t=50, b=50, l=50, r=20),
            height=350,
            autosize=True
        )
        
        # Use config for responsive charts
        config = {'displayModeBar': True, 'responsive': True, 'displaylogo': False}
        st.plotly_chart(fig, use_container_width=True, config=config)
    
    @staticmethod
    def _get_mode_emoji(mode: str) -> str:
        """Get emoji for transport mode"""
        emoji_map = {
            'Flight': '✈️',
            'Train': '🚂',
            'Car': '🚗',
            'Bus': '🚌'
        }
        return emoji_map.get(mode, '🚶')
    
    @staticmethod
    def _create_individual_route_map(origin: str, destination: str, waypoints: List[str], 
                                     route_name: str, route_color: str,
                                     geo_manager, route_optimizer) -> Optional[Any]:
        """Create an individual map for a specific route"""
        try:
            import folium
            from streamlit_folium import st_folium
            
            origin_coords = geo_manager.get_city_coordinates(origin)
            dest_coords = geo_manager.get_city_coordinates(destination)
            
            if not origin_coords or not dest_coords:
                return None
            
            origin_lat, origin_lon = origin_coords
            dest_lat, dest_lon = dest_coords
            
            # Get route coordinates
            route_coords = route_optimizer.get_route_coordinates(origin, destination, waypoints)
            
            if len(route_coords) < 2:
                return None
            
            # Calculate center point for this specific route
            all_lats = [origin_lat, dest_lat] + [lat for lat, lon in route_coords[1:-1] if lat]
            all_lons = [origin_lon, dest_lon] + [lon for lat, lon in route_coords[1:-1] if lon]
            
            center_lat = sum(all_lats) / len(all_lats) if all_lats else (origin_lat + dest_lat) / 2
            center_lon = sum(all_lons) / len(all_lons) if all_lons else (origin_lon + dest_lon) / 2
            
            # Create map for this specific route
            m = folium.Map(
                location=[center_lat, center_lon],
                zoom_start=7 if abs(origin_lat - dest_lat) < 5 else 6,
                tiles='OpenStreetMap'
            )
            
            # Add origin marker
            folium.Marker(
                [origin_lat, origin_lon],
                popup=f"🏁 Origin: {origin}",
                tooltip=f"Start: {origin}",
                icon=folium.Icon(color='green', icon='play')
            ).add_to(m)
            
            # Add destination marker
            folium.Marker(
                [dest_lat, dest_lon],
                popup=f"🏁 Destination: {destination}",
                tooltip=f"End: {destination}",
                icon=folium.Icon(color='red', icon='stop')
            ).add_to(m)
            
            # Draw the route polyline
            folium.PolyLine(
                locations=[[lat, lon] for lat, lon in route_coords],
                color=route_color,
                weight=4,
                opacity=0.8,
                popup=f"{route_name}: {origin} → {destination}",
                tooltip=route_name
            ).add_to(m)
            
            # Add waypoint markers
            for waypoint_idx, waypoint in enumerate(waypoints):
                waypoint_coords = geo_manager.get_city_coordinates(waypoint)
                if waypoint_coords:
                    wp_lat, wp_lon = waypoint_coords
                    folium.Marker(
                        [wp_lat, wp_lon],
                        popup=f"📍 Waypoint {waypoint_idx + 1}: {waypoint}",
                        tooltip=f"{waypoint}",
                        icon=folium.Icon(color='lightblue', icon='info-sign')
                    ).add_to(m)
            
            return m
            
        except Exception:
            return None
    
    @staticmethod
    def render_route_map(alternatives: List[Dict[str, Any]], origin: str, destination: str) -> None:
        """Embed interactive maps - one separate map for each route displayed in the left panel"""
        try:
            import folium
            from streamlit_folium import st_folium
            
            # Get coordinates for origin and destination
            from .geographic_data import GeographicDataManager
            from .route_optimizer import RouteOptimizer
            from .carbon_calculator import CarbonCalculator
            
            geo_manager = GeographicDataManager()
            route_optimizer = RouteOptimizer()
            carbon_calculator = CarbonCalculator()
            
            origin_coords = geo_manager.get_city_coordinates(origin)
            dest_coords = geo_manager.get_city_coordinates(destination)
            
            if not origin_coords or not dest_coords:
                st.warning("⚠️ Could not load map: City coordinates not available")
                return
            
            # Generate alternate routes with waypoints (more routes for better options)
            alternate_routes = route_optimizer.generate_alternate_routes(origin, destination, num_routes=5)
            
            # Calculate detailed route information for each route
            route_details_list = []
            direct_distance = None
            
            for idx, route_info in enumerate(alternate_routes):
                waypoints = route_info.get('waypoints', [])
                route_name = route_info.get('name', f'Route {idx + 1}')
                description = route_info.get('description', '')
                
                # Calculate route distance
                route_distance = route_optimizer.calculate_route_distance(
                    origin, destination, waypoints
                )
                
                if direct_distance is None and not waypoints:
                    direct_distance = route_distance
                
                # Calculate carbon footprint for different modes
                # Using simplified calculation (distance * emission_factor)
                emission_factors = {
                    'Car': 0.12,  # kg CO2e per km per person
                    'Bus': 0.08,
                    'Train': 0.04,
                    'Flight': 0.25
                }
                
                # Estimate carbon for different transport modes (for 1 person)
                carbon_estimates = {}
                for mode, factor in emission_factors.items():
                    carbon_estimates[mode] = route_distance * factor
                
                # Determine if this is a shortcut
                is_shortcut = False
                distance_savings = 0
                if direct_distance and route_distance < direct_distance * 0.98:  # 2% tolerance
                    is_shortcut = True
                    distance_savings = direct_distance - route_distance
                
                # Calculate efficiency score (lower distance = higher efficiency)
                efficiency_score = 100.0
                if direct_distance and direct_distance > 0:
                    efficiency_score = (direct_distance / route_distance) * 100 if route_distance > 0 else 100
                
                route_details_list.append({
                    'index': idx,
                    'name': route_name,
                    'waypoints': waypoints,
                    'description': description,
                    'distance_km': route_distance,
                    'carbon_estimates': carbon_estimates,
                    'is_shortcut': is_shortcut,
                    'distance_savings': distance_savings,
                    'efficiency_score': efficiency_score
                })
            
            # Sort routes by distance (shortest first)
            route_details_list.sort(key=lambda x: x['distance_km'])
            
            # Route colors for different alternatives
            route_colors = ['blue', 'purple', 'orange', 'darkgreen', 'darkblue']
            
            # Display route information
            st.subheader("🗺️ Route Maps with Alternate Routes & Efficiency Plan")
            st.markdown(f"**Route:** {origin} → {destination}")
            st.markdown("---")
            
            # Display each route with its own individual map
            for route_detail in route_details_list:
                idx = route_detail['index']
                waypoints = route_detail['waypoints']
                route_name = route_detail['name']
                distance = route_detail['distance_km']
                description = route_detail['description']
                carbon_estimates = route_detail['carbon_estimates']
                is_shortcut = route_detail['is_shortcut']
                distance_savings = route_detail['distance_savings']
                efficiency_score = route_detail['efficiency_score']
                route_color = route_colors[idx % len(route_colors)]
                
                # Route card with two columns: details on left, map on right
                with st.container():
                    st.markdown(f"""
                    <div style="border: 2px solid {route_color}; 
                                border-radius: 10px; padding: 15px; margin-bottom: 20px;
                                background-color: {'#e8f5e9' if is_shortcut else '#f5f5f5'};">
                    <h3 style="color: {route_color}; margin-top: 0;">
                        {route_name}
                    </h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create two columns for each route: details left, map right
                    col_details, col_map = st.columns([1.2, 1.8])
                    
                    with col_details:
                        # Route path
                        if waypoints:
                            waypoints_str = " → ".join(waypoints)
                            route_str = f"{origin} → **{waypoints_str}** → {destination}"
                        else:
                            route_str = f"{origin} → {destination}"
                        
                        st.markdown(f"**📍 Path:** {route_str}")
                        
                        # Distance and efficiency
                        col_dist, col_eff = st.columns(2)
                        with col_dist:
                            st.metric("Distance", f"{distance:.1f} km")
                        with col_eff:
                            st.metric("Efficiency", f"{efficiency_score:.1f}%")
                        
                        # Shortcut indicator
                        if is_shortcut:
                            st.success(f"✨ Shortcut! Saves {distance_savings:.1f} km ({((distance_savings/direct_distance)*100):.1f}%)")
                        
                        # Waypoints info
                        if waypoints:
                            st.markdown(f"**📍 Places Covered:** {len(waypoints)} cities")
                            for wp_idx, wp in enumerate(waypoints, 1):
                                st.markdown(f"  {wp_idx}. {wp}")
                        else:
                            st.markdown("**📍 Places Covered:** Direct route (no intermediate stops)")
                        
                        # Carbon footprint estimates
                        st.markdown("**🌱 Carbon Footprint (CO₂e):**")
                        carbon_data = []
                        for mode, co2e in carbon_estimates.items():
                            carbon_data.append(f"- {mode}: {co2e:.2f} kg")
                        st.markdown("\n".join(carbon_data))
                        
                        # Description
                        if description:
                            st.markdown(f"*💡 {description}*")
                    
                    with col_map:
                        # Create and display individual map for this route
                        route_map = VisualizationComponents._create_individual_route_map(
                            origin, destination, waypoints, route_name, route_color,
                            geo_manager, route_optimizer
                        )
                        
                        if route_map:
                            st.markdown(f"**🗺️ {route_name} Map**")
                            st_folium(route_map, width=None, height=400, returned_objects=[])
                        else:
                            st.warning("⚠️ Map unavailable for this route")
                    
                    st.markdown("---")
            
            # Summary statistics section
            st.markdown("### 📊 Route Summary")
            col1, col2, col3 = st.columns(3)
            
            shortest_distance = min(r['distance_km'] for r in route_details_list)
            longest_distance = max(r['distance_km'] for r in route_details_list)
            avg_distance = sum(r['distance_km'] for r in route_details_list) / len(route_details_list)
            
            with col1:
                st.metric("Shortest Route", f"{shortest_distance:.1f} km")
            with col2:
                st.metric("Longest Route", f"{longest_distance:.1f} km")
            with col3:
                st.metric("Average Distance", f"{avg_distance:.1f} km")
            
            # Best option recommendation
            best_route = min(route_details_list, key=lambda x: x['distance_km'])
            st.info(f"🏆 **Recommended:** {best_route['name']} ({best_route['distance_km']:.1f} km) - Most efficient route with lowest carbon footprint")
            
        except ImportError:
            st.warning("⚠️ Map display requires folium and streamlit-folium packages")
        except Exception as e:
            st.error(f"⚠️ Could not display map: {str(e)}")
            import traceback
            with st.expander("🔍 Error Details"):
                st.code(traceback.format_exc())
    
    @staticmethod
    def render_india_travel_tips() -> None:
        """Include India-specific travel tips and recommendations"""
        st.subheader("🇮🇳 India-Specific Travel Tips & Sustainable Recommendations")
        
        # Create tabs for different categories of tips
        tab1, tab2, tab3, tab4 = st.tabs(["🚂 Rail Travel", "🚌 Bus Travel", "✈️ Air Travel", "🌱 Eco Tips"])
        
        with tab1:
            st.markdown("""
            **Indian Railways - Sustainable & Affordable**
            
            🌟 **Why Choose Trains:**
            - Lowest carbon footprint among motorized transport
            - Extensive network connecting 7,000+ stations
            - Cost-effective for long distances
            - Comfortable overnight journeys available
            
            💡 **Pro Tips:**
            - Book Tatkal tickets for last-minute travel
            - Choose AC 3-Tier for comfort-cost balance
            - Rajdhani/Shatabdi for premium experience
            - Use IRCTC app for easy booking
            
            🌱 **Eco Benefits:**
            - 75% lower emissions than flights
            - 60% lower than car travel
            - Supports public transportation infrastructure
            """)
        
        with tab2:
            st.markdown("""
            **Bus Travel - Budget-Friendly Green Option**
            
            🌟 **Why Choose Buses:**
            - Second-lowest carbon footprint
            - Extensive private operator networks
            - Affordable for all budgets
            - Direct connectivity to smaller cities
            
            💡 **Pro Tips:**
            - Book Volvo/Mercedes for comfort
            - Choose overnight buses for long distances
            - Use RedBus, AbhiBus for online booking
            - Prefer government buses for reliability
            
            🌱 **Eco Benefits:**
            - 50% lower emissions than cars
            - Shared transportation reduces traffic
            - Supports local economies
            """)
        
        with tab3:
            st.markdown("""
            **Air Travel - When Speed Matters**
            
            ⚠️ **Environmental Impact:**
            - Highest carbon footprint per km
            - Consider for distances >1500km only
            - Offset emissions when possible
            
            💡 **Sustainable Flying Tips:**
            - Choose direct flights (avoid connections)
            - Fly economy class (lower per-person impact)
            - Pack light to reduce fuel consumption
            - Consider carbon offset programs
            
            🌱 **Alternatives to Consider:**
            - Train for distances <1000km
            - Overnight trains for 1000-1500km routes
            - Combine train+bus for complex routes
            """)
        
        with tab4:
            st.markdown("""
            **General Eco-Travel Tips for India**
            
            🌱 **Sustainable Practices:**
            - Carry reusable water bottles (avoid plastic)
            - Use public transport in cities
            - Choose eco-certified hotels
            - Support local businesses and food
            
            🚶 **Local Transportation:**
            - Use metro systems in major cities
            - Try cycle rickshaws for short distances
            - Walk when possible (great for exploration)
            - Use app-based shared rides
            
            🏨 **Accommodation Tips:**
            - Choose hotels with green certifications
            - Opt for homestays to support locals
            - Reuse towels and linens
            - Turn off AC/lights when not in room
            
            📱 **Useful Apps:**
            - IRCTC (train bookings)
            - RedBus (bus bookings)
            - Ola/Uber (shared rides)
            - Google Maps (public transport routes)
            """)
        
        # Add carbon offset information
        st.markdown("---")
        st.markdown("""
        ### 🌳 Carbon Offset Options in India
        
        Consider offsetting your travel emissions through:
        - **Tree plantation drives** in your local area
        - **Renewable energy projects** supporting solar/wind farms
        - **Clean cooking initiatives** providing efficient stoves
        - **Forest conservation programs** protecting biodiversity
        
        *Typical offset cost: ₹200-500 per ton of CO₂e*
        """)
    
    @staticmethod
    def render_alternatives_dashboard(alternatives: List[Dict[str, Any]], origin: str, destination: str) -> None:
        """Render complete alternatives dashboard with table, map, and tips"""
        if not alternatives:
            st.info("💡 Complete the trip form above to see alternative route suggestions")
            return
        
        # Main alternatives table
        VisualizationComponents.render_alternatives_table(alternatives)
        
        # Interactive map
        VisualizationComponents.render_route_map(alternatives, origin, destination)
        
        # India-specific travel tips
        VisualizationComponents.render_india_travel_tips()