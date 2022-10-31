from math import radians, cos, sin, asin, sqrt
_AVG_EARTH_RADIUS_KM = 6371.0088


def haversine(point1, point2):

    avg_earth_radius = _AVG_EARTH_RADIUS_KM

    lat1, lng1 = point1
    lat2, lng2 = point2

    # convert all latitudes/longitudes from decimal degrees to radians
    lat1, lng1, lat2, lng2 = map(radians, (lat1, lng1, lat2, lng2))

    # calculate haversine
    lat = lat2 - lat1
    lng = lng2 - lng1
    d = sin(lat * 0.5) ** 2 + cos(lat1) * cos(lat2) * sin(lng * 0.5) ** 2

    return 2 * avg_earth_radius * asin(sqrt(d))
