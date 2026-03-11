import math

def test_haversine():
    # London to Paris (approx 344km)
    dist = haversine(51.5074, -0.1278, 48.8566, 2.3522)
    print(f"London to Paris: {dist:.2f} km")
    assert 340 < dist < 350
    
    # 10km Test
    dist = haversine(12.9716, 77.5946, 13.0000, 77.6000)
    print(f"Bangalore Point A to B: {dist:.2f} km")
    assert dist < 10

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

if __name__ == "__main__":
    test_haversine()
    print("Haversine tests passed!")
