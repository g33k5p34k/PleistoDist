import math

def haversine(lat1,lon1,lat2,lon2):
    R = 6371
    psi1 = lat1 * math.pi/180
    psi2 = lat2 * math.pi/180
    deltapsi = (lat2 - lat1) * math.pi/180
    deltalambda = (lon2 - lon1) * math.pi/180

    a = math.sin(deltapsi/2) * math.sin(deltapsi/2) + math.cos(psi1) * math.cos(psi2) * math.sin(deltalambda/2) * math.sin(deltalambda/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d