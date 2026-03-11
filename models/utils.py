import math

def haversine(lat1, lon1, lat2, lon2):
    # Handle None values and convert to float
    try:
        if None in [lat1, lon1, lat2, lon2]:
            return 999.9 # Return large distance if coordinates missing
        
        lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
        
        # Radius of the Earth in km
        R = 6371.0
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    except:
        return 999.9
