"""
Data models for EcoTrip Planner

Contains dataclasses and data structures for trip data, emissions results,
alternative routes, and geographic locations.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime, date
import json
from geopy.distance import geodesic


@dataclass
class TripData:
    """User input containing origin, destination, dates, travel modes, and preferences"""
    origin_city: str
    destination_city: str
    outbound_date: date
    return_date: Optional[date]
    travel_modes: List[str]  # ['Flight', 'Train', 'Car', 'Bus']
    num_travelers: int
    hotel_nights: int
    
    def validate(self) -> bool:
        """Validate trip data integrity"""
        # Check required fields are not empty
        if not self.origin_city or not self.destination_city:
            return False
        
        # Check number of travelers is positive
        if self.num_travelers < 1:
            return False
        
        # Check hotel nights is non-negative
        if self.hotel_nights < 0:
            return False
        
        # Check travel modes are valid
        valid_modes = {'Flight', 'Train', 'Car', 'Bus'}
        if not all(mode in valid_modes for mode in self.travel_modes):
            return False
        
        # Check that we have either travel modes or hotel nights (or both)
        if not self.travel_modes and self.hotel_nights <= 0:
            return False
        
        # Check return date is not before outbound date if provided
        if self.return_date and self.return_date < self.outbound_date:
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for session state storage"""
        data = asdict(self)
        # Convert dates to ISO format strings for JSON serialization (handle both date and string)
        if isinstance(self.outbound_date, date):
            data['outbound_date'] = self.outbound_date.isoformat()
        elif isinstance(self.outbound_date, str):
            data['outbound_date'] = self.outbound_date
        else:
            data['outbound_date'] = str(self.outbound_date)
        
        if self.return_date:
            if isinstance(self.return_date, date):
                data['return_date'] = self.return_date.isoformat()
            elif isinstance(self.return_date, str):
                data['return_date'] = self.return_date
            else:
                data['return_date'] = str(self.return_date)
        else:
            data['return_date'] = None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TripData':
        """Create instance from dictionary"""
        # Convert date strings back to date objects
        outbound_date = date.fromisoformat(data['outbound_date'])
        return_date = date.fromisoformat(data['return_date']) if data['return_date'] else None
        
        return cls(
            origin_city=data['origin_city'],
            destination_city=data['destination_city'],
            outbound_date=outbound_date,
            return_date=return_date,
            travel_modes=data['travel_modes'],
            num_travelers=data['num_travelers'],
            hotel_nights=data['hotel_nights']
        )


@dataclass
class EmissionsResult:
    """Calculated carbon footprint data with total and breakdown values"""
    total_co2e_kg: float
    transport_emissions: Dict[str, float]  # by mode
    accommodation_emissions: float
    per_person_emissions: float
    calculation_timestamp: datetime
    calculation_warnings: Optional[List[str]] = None
    
    def get_breakdown_percentages(self) -> Dict[str, float]:
        """Calculate percentage breakdown of emissions"""
        if self.total_co2e_kg == 0:
            return {'transport': 0.0, 'accommodation': 0.0}
        
        transport_total = sum(self.transport_emissions.values())
        transport_percentage = (transport_total / self.total_co2e_kg) * 100
        accommodation_percentage = (self.accommodation_emissions / self.total_co2e_kg) * 100
        
        return {
            'transport': round(transport_percentage, 2),
            'accommodation': round(accommodation_percentage, 2)
        }
    
    def has_warnings(self) -> bool:
        """Check if there are any calculation warnings"""
        return bool(self.calculation_warnings)
    
    def get_warning_summary(self) -> str:
        """Get a summary of all warnings"""
        if not self.calculation_warnings:
            return ""
        return "; ".join(self.calculation_warnings)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for session state storage"""
        data = asdict(self)
        # Convert datetime to ISO format string (handle both datetime and string)
        if isinstance(self.calculation_timestamp, datetime):
            data['calculation_timestamp'] = self.calculation_timestamp.isoformat()
        elif isinstance(self.calculation_timestamp, str):
            # Already a string, keep it as is
            data['calculation_timestamp'] = self.calculation_timestamp
        else:
            # Fallback: convert to string
            data['calculation_timestamp'] = str(self.calculation_timestamp)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmissionsResult':
        """Create instance from dictionary"""
        # Convert timestamp string back to datetime object (handle both string and datetime)
        timestamp = data.get('calculation_timestamp')
        if isinstance(timestamp, str):
            calculation_timestamp = datetime.fromisoformat(timestamp)
        elif isinstance(timestamp, datetime):
            calculation_timestamp = timestamp
        else:
            # Fallback to current time
            calculation_timestamp = datetime.now()
        
        return cls(
            total_co2e_kg=data['total_co2e_kg'],
            transport_emissions=data['transport_emissions'],
            accommodation_emissions=data['accommodation_emissions'],
            per_person_emissions=data['per_person_emissions'],
            calculation_timestamp=calculation_timestamp,
            calculation_warnings=data.get('calculation_warnings')
        )


@dataclass
class AlternativeRoute:
    """Suggested travel option with different mode, time, cost, and emissions"""
    transport_mode: str
    duration_hours: float
    distance_km: float
    co2e_emissions_kg: float
    estimated_cost_inr: float
    emissions_savings_kg: float
    cost_difference_inr: float
    route_details: Dict[str, Any]
    
    def calculate_savings_percentage(self, baseline: float) -> float:
        """Calculate percentage savings vs baseline"""
        if baseline == 0:
            return 0.0
        return round((self.emissions_savings_kg / baseline) * 100, 2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for session state storage"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AlternativeRoute':
        """Create instance from dictionary"""
        return cls(**data)


@dataclass
class GeographicLocation:
    """Geographic location data for Indian cities"""
    city_name: str
    state: str
    latitude: float
    longitude: float
    popular_destinations: List[str]
    
    def calculate_distance_to(self, other: 'GeographicLocation') -> float:
        """Calculate geodesic distance to another location"""
        point1 = (self.latitude, self.longitude)
        point2 = (other.latitude, other.longitude)
        return geodesic(point1, point2).kilometers
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for session state storage"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeographicLocation':
        """Create instance from dictionary"""
        return cls(**data)