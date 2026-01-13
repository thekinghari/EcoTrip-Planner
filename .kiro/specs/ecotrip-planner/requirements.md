# Requirements Document

## Introduction

EcoTrip Planner is a web application that helps users in India make sustainable travel decisions by calculating carbon emissions for their trips and suggesting greener alternatives. The application provides real-time carbon footprint calculations, visualizations, and alternative route recommendations to promote eco-friendly travel choices.

## Glossary

- **Carbon_Calculator**: Component that computes CO₂ emissions for travel and accommodation
- **Trip_Data**: User input containing origin, destination, dates, travel modes, and preferences
- **Emissions_Result**: Calculated carbon footprint data with total and breakdown values
- **Alternative_Route**: Suggested travel option with different mode, time, cost, and emissions
- **Visualization_Dashboard**: Interactive charts and graphs displaying emissions data
- **User_Interface**: Streamlit-based web interface for user interactions
- **API_Service**: External service integration (Climatiq, Google Maps) for data retrieval
- **Session_State**: Temporary data storage mechanism within user session

## Requirements

### Requirement 1: Trip Input Collection

**User Story:** As a traveler, I want to input my trip details through an interactive form, so that I can get personalized carbon footprint calculations.

#### Acceptance Criteria

1. WHEN a user accesses the application, THE User_Interface SHALL display an interactive form with all required input fields
2. WHEN a user selects origin and destination cities, THE User_Interface SHALL provide default values of "Salem" and "Chennai" respectively
3. WHEN a user selects travel dates, THE User_Interface SHALL accept both outbound and return date inputs using date picker controls
4. WHEN a user selects travel modes, THE User_Interface SHALL provide multiselect options including Flight, Train, Car, and Bus
5. WHEN a user specifies number of travelers, THE User_Interface SHALL accept numeric input with minimum value of 1
6. WHEN a user specifies hotel nights, THE User_Interface SHALL accept numeric input with minimum value of 0
7. WHEN a user selects from popular routes, THE User_Interface SHALL auto-populate origin and destination fields with predefined city pairs
8. WHEN a user submits the form, THE User_Interface SHALL store all input data in session state as a structured dictionary

### Requirement 2: Carbon Footprint Calculation

**User Story:** As an environmentally conscious traveler, I want to know the carbon emissions of my trip, so that I can understand my environmental impact.

#### Acceptance Criteria

1. WHEN trip data is submitted, THE Carbon_Calculator SHALL retrieve emissions factors from the Climatiq API for accurate calculations
2. IF the Climatiq API is unavailable, THEN THE Carbon_Calculator SHALL use predefined emission factors as fallback values
3. WHEN calculating transport emissions, THE Carbon_Calculator SHALL compute distance using geographic coordinates of Indian cities
4. WHEN calculating total emissions, THE Carbon_Calculator SHALL include both transportation and accommodation components
5. WHEN processing multiple travelers, THE Carbon_Calculator SHALL multiply per-person emissions by the number of travelers
6. WHEN calculations are complete, THE Carbon_Calculator SHALL return structured results with total emissions and detailed breakdown
7. WHEN results are generated, THE Carbon_Calculator SHALL store emissions data in session state for visualization

### Requirement 3: Data Visualization

**User Story:** As a user, I want to see visual representations of my carbon footprint, so that I can easily understand and compare my environmental impact.

#### Acceptance Criteria

1. WHEN emissions data is available, THE Visualization_Dashboard SHALL display a pie chart showing breakdown between transport and accommodation emissions
2. WHEN displaying comparisons, THE Visualization_Dashboard SHALL show a bar chart comparing trip emissions against average Indian domestic trip benchmarks
3. WHEN presenting results, THE Visualization_Dashboard SHALL include textual comparisons with specific emission values and percentages
4. WHEN charts are rendered, THE Visualization_Dashboard SHALL use interactive Plotly components for enhanced user experience
5. WHEN data updates occur, THE Visualization_Dashboard SHALL refresh visualizations in real-time

### Requirement 4: Alternative Route Suggestions

**User Story:** As a traveler seeking greener options, I want to see alternative travel routes with lower carbon emissions, so that I can make more sustainable choices.

#### Acceptance Criteria

1. WHEN generating alternatives, THE API_Service SHALL query Google Maps Directions API for different transportation modes
2. WHEN processing route data, THE Carbon_Calculator SHALL compute emissions for each alternative using the same calculation engine
3. WHEN calculating costs, THE Alternative_Route SHALL estimate expenses using predefined cost factors per transportation mode
4. WHEN displaying alternatives, THE User_Interface SHALL present results in a structured table format with mode, time, distance, emissions, savings, and cost columns
5. WHEN showing routes, THE User_Interface SHALL embed an interactive map displaying origin, destination, and route markers
6. WHEN comparing options, THE Alternative_Route SHALL calculate emission savings relative to the original trip selection

### Requirement 5: Session Management

**User Story:** As a user, I want my trip data and calculations to persist during my session, so that I can review and modify my travel plans without losing information.

#### Acceptance Criteria

1. WHEN a user inputs trip data, THE User_Interface SHALL store all information in session state without requiring database persistence
2. WHEN calculations are performed, THE User_Interface SHALL maintain emissions results throughout the session
3. WHEN users navigate between different views, THE User_Interface SHALL preserve all previously entered data and calculated results
4. WHEN sessions expire or users refresh, THE User_Interface SHALL clear all stored data and reset to initial state

### Requirement 6: API Integration and Error Handling

**User Story:** As a user, I want the application to work reliably even when external services are unavailable, so that I can always get carbon footprint estimates.

#### Acceptance Criteria

1. WHEN integrating with external APIs, THE API_Service SHALL use environment variables for secure API key management
2. WHEN API requests fail, THE API_Service SHALL implement graceful fallback mechanisms using static data
3. WHEN errors occur, THE User_Interface SHALL display user-friendly error messages without exposing technical details
4. WHEN API rate limits are reached, THE API_Service SHALL automatically switch to fallback calculation methods
5. WHEN network issues arise, THE User_Interface SHALL continue functioning with cached or static data

### Requirement 7: User Experience and Interface Design

**User Story:** As a user, I want an intuitive and visually appealing interface with eco-friendly design elements, so that I have a pleasant experience while learning about sustainable travel.

#### Acceptance Criteria

1. WHEN users access the application, THE User_Interface SHALL display an eco-themed design using green color schemes and environmental emojis
2. WHEN forms are presented, THE User_Interface SHALL provide clear labels, helpful tooltips, and validation feedback
3. WHEN calculations are in progress, THE User_Interface SHALL show loading indicators and progress feedback
4. WHEN displaying results, THE User_Interface SHALL organize information in logical sections with clear headings and spacing
5. WHEN providing recommendations, THE User_Interface SHALL include India-specific travel tips and sustainable transportation advice

### Requirement 8: Geographic Data Management

**User Story:** As a user traveling within India, I want accurate distance calculations between cities, so that my carbon footprint estimates are reliable.

#### Acceptance Criteria

1. WHEN calculating distances, THE Carbon_Calculator SHALL use precise geographic coordinates for major Indian cities
2. WHEN users select cities, THE User_Interface SHALL provide a comprehensive list of popular Indian destinations
3. WHEN computing routes, THE Carbon_Calculator SHALL use geodesic distance calculations for accuracy
4. WHEN handling city data, THE User_Interface SHALL support both manual input and predefined city selection