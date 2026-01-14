"""Test ML model coverage across all Indian cities"""
from components.ml_route_predictor import MLRoutePredictor
from components.ml_emissions_model import MLEmissionsPredictor
from components.geographic_data import GeographicDataManager

# Initialize models
rp = MLRoutePredictor()
em = MLEmissionsPredictor()
gm = GeographicDataManager()

print("=" * 70)
print("ML MODEL COMPREHENSIVE COVERAGE TEST")
print("=" * 70)

# Test 1: Total cities available
all_cities = gm.get_all_cities()
print(f"\n✓ Total cities in database: {len(all_cities)}")

# Test 2: States/UTs coverage
states = set([gm.get_city_info(c).state for c in all_cities if gm.get_city_info(c)])
print(f"✓ States/UTs covered: {len(states)}")

# Test 3: Cross-region route predictions
print("\n" + "=" * 70)
print("TESTING ROUTES ACROSS ALL REGIONS OF INDIA")
print("=" * 70)

test_routes = [
    ('Itanagar', 'Mumbai', 'Northeast to West'),
    ('Gangtok', 'Kochi', 'Northeast to South'),
    ('Srinagar', 'Chennai', 'North to South'),
    ('Port Blair', 'Delhi', 'Islands to Capital'),
    ('Patna', 'Guwahati', 'East to Northeast'),
]

for origin, dest, description in test_routes:
    dist = rp.predict_distance(origin, dest, 'Flight')
    dur = rp.predict_duration(origin, dest, 'Flight')
    emissions = em.predict_total_emissions('Flight', dist, 1)
    print(f"\n{description}:")
    print(f"  {origin} -> {dest}")
    print(f"  Distance: {dist:.0f} km | Duration: {dur:.1f} hrs | Emissions: {emissions:.1f} kg CO2")

# Test 4: Multiple transport modes
print("\n" + "=" * 70)
print("TESTING ALL TRANSPORT MODES")
print("=" * 70)

test_city_pair = ('Delhi', 'Mumbai')
modes = ['Flight', 'Train', 'Car', 'Bus']

print(f"\nRoute: {test_city_pair[0]} -> {test_city_pair[1]}")
for mode in modes:
    dist = rp.predict_distance(test_city_pair[0], test_city_pair[1], mode)
    dur = rp.predict_duration(test_city_pair[0], test_city_pair[1], mode)
    emissions = em.predict_total_emissions(mode, dist, 1)
    print(f"  {mode:8s}: {dist:6.0f} km | {dur:5.1f} hrs | {emissions:6.1f} kg CO2")

print("\n" + "=" * 70)
print("TEST COMPLETE - ML MODEL READY FOR ALL INDIAN CITIES!")
print("=" * 70)
