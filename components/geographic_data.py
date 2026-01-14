"""
Geographic data management for EcoTrip Planner

Manages Indian city coordinates, distance calculations, and location services.
"""

from typing import Dict, List, Tuple, Optional
from geopy.distance import geodesic
from pathlib import Path
import csv
from .models import GeographicLocation


class GeographicDataManager:
    """Manages geographic data and distance calculations for Indian cities"""
    
    def __init__(self):
        # Base Indian cities database with coordinates (200+ major cities across all states)
        # For full coverage of Indian cities/towns, this in-code list can be extended at runtime
        # from an external CSV file (see _load_additional_cities_from_csv).
        self.indian_cities = {
            # Andhra Pradesh
            'Visakhapatnam': GeographicLocation('Visakhapatnam', 'Andhra Pradesh', 17.6869, 83.2185, []),
            'Vijayawada': GeographicLocation('Vijayawada', 'Andhra Pradesh', 16.5062, 80.6480, []),
            'Guntur': GeographicLocation('Guntur', 'Andhra Pradesh', 16.3067, 80.4365, []),
            'Nellore': GeographicLocation('Nellore', 'Andhra Pradesh', 14.4426, 79.9865, []),
            'Kurnool': GeographicLocation('Kurnool', 'Andhra Pradesh', 15.8281, 78.0373, []),
            'Tirupati': GeographicLocation('Tirupati', 'Andhra Pradesh', 13.6288, 79.4192, []),
            'Kakinada': GeographicLocation('Kakinada', 'Andhra Pradesh', 16.9891, 82.2475, []),
            'Rajahmundry': GeographicLocation('Rajahmundry', 'Andhra Pradesh', 17.0005, 81.8040, []),
            
            # Arunachal Pradesh
            'Itanagar': GeographicLocation('Itanagar', 'Arunachal Pradesh', 27.0844, 93.6053, []),
            'Naharlagun': GeographicLocation('Naharlagun', 'Arunachal Pradesh', 27.1048, 93.6989, []),
            
            # Assam
            'Guwahati': GeographicLocation('Guwahati', 'Assam', 26.1445, 91.7362, []),
            'Silchar': GeographicLocation('Silchar', 'Assam', 24.8333, 92.7789, []),
            'Dibrugarh': GeographicLocation('Dibrugarh', 'Assam', 27.4728, 94.9120, []),
            'Jorhat': GeographicLocation('Jorhat', 'Assam', 26.7509, 94.2037, []),
            'Tezpur': GeographicLocation('Tezpur', 'Assam', 26.6338, 92.8000, []),
            
            # Bihar
            'Patna': GeographicLocation('Patna', 'Bihar', 25.5941, 85.1376, []),
            'Gaya': GeographicLocation('Gaya', 'Bihar', 24.7955, 85.0002, []),
            'Bhagalpur': GeographicLocation('Bhagalpur', 'Bihar', 25.2425, 86.9842, []),
            'Muzaffarpur': GeographicLocation('Muzaffarpur', 'Bihar', 26.1225, 85.3906, []),
            'Darbhanga': GeographicLocation('Darbhanga', 'Bihar', 26.1542, 85.8918, []),
            'Purnia': GeographicLocation('Purnia', 'Bihar', 25.7771, 87.4753, []),
            
            # Chhattisgarh
            'Raipur': GeographicLocation('Raipur', 'Chhattisgarh', 21.2514, 81.6296, []),
            'Bhilai': GeographicLocation('Bhilai', 'Chhattisgarh', 21.2095, 81.3784, []),
            'Bilaspur': GeographicLocation('Bilaspur', 'Chhattisgarh', 22.0797, 82.1409, []),
            'Korba': GeographicLocation('Korba', 'Chhattisgarh', 22.3595, 82.7501, []),
            'Durg': GeographicLocation('Durg', 'Chhattisgarh', 21.1905, 81.2849, []),
            
            # Goa
            'Panaji': GeographicLocation('Panaji', 'Goa', 15.4909, 73.8278, []),
            'Margao': GeographicLocation('Margao', 'Goa', 15.2832, 73.9667, []),
            'Vasco da Gama': GeographicLocation('Vasco da Gama', 'Goa', 15.3989, 73.8151, []),
            'Goa': GeographicLocation('Goa', 'Goa', 15.2993, 74.1240, []),
            
            # Gujarat
            'Ahmedabad': GeographicLocation('Ahmedabad', 'Gujarat', 23.0225, 72.5714, []),
            'Surat': GeographicLocation('Surat', 'Gujarat', 21.1702, 72.8311, []),
            'Vadodara': GeographicLocation('Vadodara', 'Gujarat', 22.3072, 73.1812, []),
            'Rajkot': GeographicLocation('Rajkot', 'Gujarat', 22.3039, 70.8022, []),
            'Bhavnagar': GeographicLocation('Bhavnagar', 'Gujarat', 21.7645, 72.1519, []),
            'Jamnagar': GeographicLocation('Jamnagar', 'Gujarat', 22.4707, 70.0577, []),
            'Gandhinagar': GeographicLocation('Gandhinagar', 'Gujarat', 23.2156, 72.6369, []),
            'Anand': GeographicLocation('Anand', 'Gujarat', 22.5645, 72.9289, []),
            
            # Haryana
            'Faridabad': GeographicLocation('Faridabad', 'Haryana', 28.4089, 77.3178, []),
            'Gurgaon': GeographicLocation('Gurgaon', 'Haryana', 28.4595, 77.0266, []),
            'Gurugram': GeographicLocation('Gurugram', 'Haryana', 28.4595, 77.0266, []),
            'Panipat': GeographicLocation('Panipat', 'Haryana', 29.3909, 76.9635, []),
            'Ambala': GeographicLocation('Ambala', 'Haryana', 30.3782, 76.7767, []),
            'Karnal': GeographicLocation('Karnal', 'Haryana', 29.6857, 76.9905, []),
            'Hisar': GeographicLocation('Hisar', 'Haryana', 29.1492, 75.7217, []),
            
            # Himachal Pradesh
            'Shimla': GeographicLocation('Shimla', 'Himachal Pradesh', 31.1048, 77.1734, []),
            'Manali': GeographicLocation('Manali', 'Himachal Pradesh', 32.2396, 77.1887, []),
            'Dharamshala': GeographicLocation('Dharamshala', 'Himachal Pradesh', 32.2190, 76.3234, []),
            'Kullu': GeographicLocation('Kullu', 'Himachal Pradesh', 31.9578, 77.1093, []),
            'Solan': GeographicLocation('Solan', 'Himachal Pradesh', 30.9045, 77.0967, []),
            
            # Jharkhand
            'Ranchi': GeographicLocation('Ranchi', 'Jharkhand', 23.3441, 85.3096, []),
            'Jamshedpur': GeographicLocation('Jamshedpur', 'Jharkhand', 22.8046, 86.2029, []),
            'Dhanbad': GeographicLocation('Dhanbad', 'Jharkhand', 23.7957, 86.4304, []),
            'Bokaro': GeographicLocation('Bokaro', 'Jharkhand', 23.6693, 86.1511, []),
            'Hazaribagh': GeographicLocation('Hazaribagh', 'Jharkhand', 23.9929, 85.3615, []),
            
            # Karnataka
            'Bangalore': GeographicLocation('Bangalore', 'Karnataka', 12.9716, 77.5946, []),
            'Bengaluru': GeographicLocation('Bengaluru', 'Karnataka', 12.9716, 77.5946, []),
            'Mysore': GeographicLocation('Mysore', 'Karnataka', 12.2958, 76.6394, []),
            'Mysuru': GeographicLocation('Mysuru', 'Karnataka', 12.2958, 76.6394, []),
            'Hubli': GeographicLocation('Hubli', 'Karnataka', 15.3647, 75.1240, []),
            'Mangalore': GeographicLocation('Mangalore', 'Karnataka', 12.9141, 74.8560, []),
            'Belgaum': GeographicLocation('Belgaum', 'Karnataka', 15.8497, 74.4977, []),
            'Gulbarga': GeographicLocation('Gulbarga', 'Karnataka', 17.3297, 76.8343, []),
            'Davangere': GeographicLocation('Davangere', 'Karnataka', 14.4644, 75.9218, []),
            'Bellary': GeographicLocation('Bellary', 'Karnataka', 15.1394, 76.9214, []),
            
            # Kerala
            'Thiruvananthapuram': GeographicLocation('Thiruvananthapuram', 'Kerala', 8.5241, 76.9366, []),
            'Kochi': GeographicLocation('Kochi', 'Kerala', 9.9312, 76.2673, []),
            'Kozhikode': GeographicLocation('Kozhikode', 'Kerala', 11.2588, 75.7804, []),
            'Thrissur': GeographicLocation('Thrissur', 'Kerala', 10.5276, 76.2144, []),
            'Kollam': GeographicLocation('Kollam', 'Kerala', 8.8932, 76.6141, []),
            'Kannur': GeographicLocation('Kannur', 'Kerala', 11.8745, 75.3704, []),
            'Alappuzha': GeographicLocation('Alappuzha', 'Kerala', 9.4981, 76.3388, []),
            'Palakkad': GeographicLocation('Palakkad', 'Kerala', 10.7867, 76.6548, []),
            
            # Madhya Pradesh
            'Indore': GeographicLocation('Indore', 'Madhya Pradesh', 22.7196, 75.8577, []),
            'Bhopal': GeographicLocation('Bhopal', 'Madhya Pradesh', 23.2599, 77.4126, []),
            'Jabalpur': GeographicLocation('Jabalpur', 'Madhya Pradesh', 23.1815, 79.9864, []),
            'Gwalior': GeographicLocation('Gwalior', 'Madhya Pradesh', 26.2183, 78.1828, []),
            'Ujjain': GeographicLocation('Ujjain', 'Madhya Pradesh', 23.1765, 75.7885, []),
            'Sagar': GeographicLocation('Sagar', 'Madhya Pradesh', 23.8388, 78.7378, []),
            'Dewas': GeographicLocation('Dewas', 'Madhya Pradesh', 22.9676, 76.0534, []),
            
            # Maharashtra
            'Mumbai': GeographicLocation('Mumbai', 'Maharashtra', 19.0760, 72.8777, []),
            'Pune': GeographicLocation('Pune', 'Maharashtra', 18.5204, 73.8567, []),
            'Nagpur': GeographicLocation('Nagpur', 'Maharashtra', 21.1458, 79.0882, []),
            'Thane': GeographicLocation('Thane', 'Maharashtra', 19.2183, 72.9781, []),
            'Nashik': GeographicLocation('Nashik', 'Maharashtra', 19.9975, 73.7898, []),
            'Aurangabad': GeographicLocation('Aurangabad', 'Maharashtra', 19.8762, 75.3433, []),
            'Solapur': GeographicLocation('Solapur', 'Maharashtra', 17.6599, 75.9064, []),
            'Kolhapur': GeographicLocation('Kolhapur', 'Maharashtra', 16.7050, 74.2433, []),
            'Amravati': GeographicLocation('Amravati', 'Maharashtra', 20.9374, 77.7796, []),
            'Navi Mumbai': GeographicLocation('Navi Mumbai', 'Maharashtra', 19.0330, 73.0297, []),
            
            # Manipur
            'Imphal': GeographicLocation('Imphal', 'Manipur', 24.8170, 93.9368, []),
            
            # Meghalaya
            'Shillong': GeographicLocation('Shillong', 'Meghalaya', 25.5788, 91.8933, []),
            
            # Mizoram
            'Aizawl': GeographicLocation('Aizawl', 'Mizoram', 23.7271, 92.7176, []),
            
            # Nagaland
            'Kohima': GeographicLocation('Kohima', 'Nagaland', 25.6747, 94.1086, []),
            'Dimapur': GeographicLocation('Dimapur', 'Nagaland', 25.9040, 93.7265, []),
            
            # Odisha
            'Bhubaneswar': GeographicLocation('Bhubaneswar', 'Odisha', 20.2961, 85.8245, []),
            'Cuttack': GeographicLocation('Cuttack', 'Odisha', 20.4625, 85.8830, []),
            'Rourkela': GeographicLocation('Rourkela', 'Odisha', 22.2604, 84.8536, []),
            'Puri': GeographicLocation('Puri', 'Odisha', 19.8135, 85.8312, []),
            'Berhampur': GeographicLocation('Berhampur', 'Odisha', 19.3150, 84.7941, []),
            
            # Punjab
            'Ludhiana': GeographicLocation('Ludhiana', 'Punjab', 30.9010, 75.8573, []),
            'Amritsar': GeographicLocation('Amritsar', 'Punjab', 31.6340, 74.8723, []),
            'Jalandhar': GeographicLocation('Jalandhar', 'Punjab', 31.3260, 75.5762, []),
            'Patiala': GeographicLocation('Patiala', 'Punjab', 30.3398, 76.3869, []),
            'Bathinda': GeographicLocation('Bathinda', 'Punjab', 30.2110, 74.9455, []),
            'Chandigarh': GeographicLocation('Chandigarh', 'Punjab', 30.7333, 76.7794, []),
            
            # Rajasthan
            'Jaipur': GeographicLocation('Jaipur', 'Rajasthan', 26.9124, 75.7873, []),
            'Jodhpur': GeographicLocation('Jodhpur', 'Rajasthan', 26.2389, 73.0243, []),
            'Udaipur': GeographicLocation('Udaipur', 'Rajasthan', 24.5854, 73.7125, []),
            'Kota': GeographicLocation('Kota', 'Rajasthan', 25.2138, 75.8648, []),
            'Bikaner': GeographicLocation('Bikaner', 'Rajasthan', 28.0229, 73.3119, []),
            'Ajmer': GeographicLocation('Ajmer', 'Rajasthan', 26.4499, 74.6399, []),
            'Alwar': GeographicLocation('Alwar', 'Rajasthan', 27.5530, 76.6346, []),
            'Bharatpur': GeographicLocation('Bharatpur', 'Rajasthan', 27.2152, 77.4909, []),
            
            # Sikkim
            'Gangtok': GeographicLocation('Gangtok', 'Sikkim', 27.3389, 88.6065, []),
            
            # Tamil Nadu
            'Chennai': GeographicLocation('Chennai', 'Tamil Nadu', 13.0827, 80.2707, []),
            'Coimbatore': GeographicLocation('Coimbatore', 'Tamil Nadu', 11.0168, 76.9558, []),
            'Madurai': GeographicLocation('Madurai', 'Tamil Nadu', 9.9252, 78.1198, []),
            'Tiruchirappalli': GeographicLocation('Tiruchirappalli', 'Tamil Nadu', 10.7905, 78.7047, []),
            'Trichy': GeographicLocation('Trichy', 'Tamil Nadu', 10.7905, 78.7047, []),
            'Salem': GeographicLocation('Salem', 'Tamil Nadu', 11.6643, 78.1460, []),
            'Tirunelveli': GeographicLocation('Tirunelveli', 'Tamil Nadu', 8.7139, 77.7567, []),
            'Erode': GeographicLocation('Erode', 'Tamil Nadu', 11.3410, 77.7172, []),
            'Vellore': GeographicLocation('Vellore', 'Tamil Nadu', 12.9165, 79.1325, []),
            'Thoothukudi': GeographicLocation('Thoothukudi', 'Tamil Nadu', 8.7642, 78.1348, []),
            'Thanjavur': GeographicLocation('Thanjavur', 'Tamil Nadu', 10.7870, 79.1378, []),
            'Nagercoil': GeographicLocation('Nagercoil', 'Tamil Nadu', 8.1790, 77.4337, []),
            'Kanchipuram': GeographicLocation('Kanchipuram', 'Tamil Nadu', 12.8342, 79.7036, []),
            'Pondicherry': GeographicLocation('Pondicherry', 'Tamil Nadu', 11.9416, 79.8083, []),
            
            # Telangana
            'Hyderabad': GeographicLocation('Hyderabad', 'Telangana', 17.3850, 78.4867, []),
            'Warangal': GeographicLocation('Warangal', 'Telangana', 17.9689, 79.5941, []),
            'Nizamabad': GeographicLocation('Nizamabad', 'Telangana', 18.6725, 78.0941, []),
            'Khammam': GeographicLocation('Khammam', 'Telangana', 17.2473, 80.1514, []),
            'Karimnagar': GeographicLocation('Karimnagar', 'Telangana', 18.4386, 79.1288, []),
            
            # Tripura
            'Agartala': GeographicLocation('Agartala', 'Tripura', 23.8315, 91.2868, []),
            
            # Uttar Pradesh
            'Lucknow': GeographicLocation('Lucknow', 'Uttar Pradesh', 26.8467, 80.9462, []),
            'Kanpur': GeographicLocation('Kanpur', 'Uttar Pradesh', 26.4499, 80.3319, []),
            'Agra': GeographicLocation('Agra', 'Uttar Pradesh', 27.1767, 78.0081, []),
            'Varanasi': GeographicLocation('Varanasi', 'Uttar Pradesh', 25.3176, 82.9739, []),
            'Meerut': GeographicLocation('Meerut', 'Uttar Pradesh', 28.9845, 77.7064, []),
            'Allahabad': GeographicLocation('Allahabad', 'Uttar Pradesh', 25.4358, 81.8463, []),
            'Prayagraj': GeographicLocation('Prayagraj', 'Uttar Pradesh', 25.4358, 81.8463, []),
            'Bareilly': GeographicLocation('Bareilly', 'Uttar Pradesh', 28.3670, 79.4304, []),
            'Aligarh': GeographicLocation('Aligarh', 'Uttar Pradesh', 27.8974, 78.0880, []),
            'Moradabad': GeographicLocation('Moradabad', 'Uttar Pradesh', 28.8389, 78.7378, []),
            'Ghaziabad': GeographicLocation('Ghaziabad', 'Uttar Pradesh', 28.6692, 77.4538, []),
            'Noida': GeographicLocation('Noida', 'Uttar Pradesh', 28.5355, 77.3910, []),
            'Mathura': GeographicLocation('Mathura', 'Uttar Pradesh', 27.4924, 77.6737, []),
            'Gorakhpur': GeographicLocation('Gorakhpur', 'Uttar Pradesh', 26.7606, 83.3732, []),
            
            # Uttarakhand
            'Dehradun': GeographicLocation('Dehradun', 'Uttarakhand', 30.3165, 78.0322, []),
            'Haridwar': GeographicLocation('Haridwar', 'Uttarakhand', 29.9457, 78.1642, []),
            'Rishikesh': GeographicLocation('Rishikesh', 'Uttarakhand', 30.0869, 78.2676, []),
            'Nainital': GeographicLocation('Nainital', 'Uttarakhand', 29.3803, 79.4636, []),
            'Roorkee': GeographicLocation('Roorkee', 'Uttarakhand', 29.8543, 77.8880, []),
            
            # West Bengal
            'Kolkata': GeographicLocation('Kolkata', 'West Bengal', 22.5726, 88.3639, []),
            'Howrah': GeographicLocation('Howrah', 'West Bengal', 22.5958, 88.2636, []),
            'Durgapur': GeographicLocation('Durgapur', 'West Bengal', 23.5204, 87.3119, []),
            'Asansol': GeographicLocation('Asansol', 'West Bengal', 23.6739, 86.9524, []),
            'Siliguri': GeographicLocation('Siliguri', 'West Bengal', 26.7271, 88.3953, []),
            'Darjeeling': GeographicLocation('Darjeeling', 'West Bengal', 27.0410, 88.2663, []),
            
            # Union Territories
            'Delhi': GeographicLocation('Delhi', 'Delhi', 28.7041, 77.1025, []),
            'New Delhi': GeographicLocation('New Delhi', 'Delhi', 28.6139, 77.2090, []),
            'Puducherry': GeographicLocation('Puducherry', 'Puducherry', 11.9416, 79.8083, []),
            'Port Blair': GeographicLocation('Port Blair', 'Andaman and Nicobar Islands', 11.6234, 92.7265, []),
            'Leh': GeographicLocation('Leh', 'Ladakh', 34.1526, 77.5771, []),
            'Srinagar': GeographicLocation('Srinagar', 'Jammu and Kashmir', 34.0837, 74.7973, []),
            'Jammu': GeographicLocation('Jammu', 'Jammu and Kashmir', 32.7266, 74.8570, []),
            'Daman': GeographicLocation('Daman', 'Dadra and Nagar Haveli and Daman and Diu', 20.4283, 72.8397, []),
            'Silvassa': GeographicLocation('Silvassa', 'Dadra and Nagar Haveli and Daman and Diu', 20.2737, 73.0135, [])
        }

        # Optionally extend with a much larger set of cities from CSV (if present).
        # This lets you support "all cities in India" without bloating the source code.
        self._load_additional_cities_from_csv()

    def _load_additional_cities_from_csv(self) -> None:
        """Load additional Indian cities from an external CSV file, if available.

        Expected file location (relative to project root):
          data/indian_cities.csv

        Expected columns (header row required):
          city,state,latitude,longitude
        """
        try:
            # components/geographic_data.py -> project root (two levels up)
            project_root = Path(__file__).resolve().parents[1]
            data_path = project_root / "data" / "indian_cities.csv"

            if not data_path.exists():
                return

            with data_path.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    city = (row.get("city") or "").strip()
                    state = (row.get("state") or "").strip()
                    lat_str = (row.get("latitude") or "").strip()
                    lon_str = (row.get("longitude") or "").strip()

                    if not city or not state or not lat_str or not lon_str:
                        continue

                    try:
                        lat = float(lat_str)
                        lon = float(lon_str)
                    except ValueError:
                        # Skip rows with invalid numeric coordinates
                        continue

                    # Do not overwrite curated in-code entries
                    if city not in self.indian_cities:
                        self.indian_cities[city] = GeographicLocation(
                            city, state, lat, lon, []
                        )
        except Exception:
            # Fail silently so any CSV issues don't break the app;
            # the built-in base city list will still be used.
            return
        
        # Popular route pairs for quick selection
        self.popular_routes = [
            ('Salem', 'Chennai'),
            ('Delhi', 'Mumbai'),
            ('Bangalore', 'Chennai'),
            ('Delhi', 'Goa'),
            ('Mumbai', 'Pune'),
            ('Chennai', 'Kochi'),
            ('Delhi', 'Jaipur'),
            ('Mumbai', 'Goa'),
            ('Bangalore', 'Hyderabad'),
            ('Kolkata', 'Delhi')
        ]
    
    def get_city_coordinates(self, city_name: str) -> Optional[Tuple[float, float]]:
        """Retrieve latitude/longitude for a city"""
        city = self.indian_cities.get(city_name)
        if city:
            return (city.latitude, city.longitude)
        return None
    
    def calculate_geodesic_distance(self, origin: str, destination: str) -> Optional[float]:
        """Calculate accurate distance between two cities in kilometers"""
        origin_coords = self.get_city_coordinates(origin)
        destination_coords = self.get_city_coordinates(destination)
        
        if origin_coords and destination_coords:
            distance = geodesic(origin_coords, destination_coords).kilometers
            return distance
        
        return None
    
    def validate_city_names(self, city_name: str) -> bool:
        """Check if city name exists in the database"""
        return city_name in self.indian_cities
    
    def get_city_suggestions(self, partial_name: str) -> List[str]:
        """Get city name suggestions for partial matches"""
        partial_lower = partial_name.lower()
        suggestions = [
            city for city in self.indian_cities.keys()
            if partial_lower in city.lower()
        ]
        return suggestions[:5]  # Return top 5 matches
    
    def get_popular_routes(self) -> List[Tuple[str, str]]:
        """Get list of popular route pairs"""
        return self.popular_routes
    
    def get_all_cities(self) -> List[str]:
        """Get list of all available cities"""
        return list(self.indian_cities.keys())
    
    def get_city_info(self, city_name: str) -> Optional[GeographicLocation]:
        """Get complete city information"""
        return self.indian_cities.get(city_name)
    
    def calculate_distance(self, origin: str, destination: str) -> float:
        """Calculate distance between two cities in kilometers (alias for calculate_geodesic_distance)"""
        distance = self.calculate_geodesic_distance(origin, destination)
        return distance if distance is not None else 0.0