"""
>>> x, y = project(deg2rad(0), deg2rad(0), deg2rad(0), deg2rad(0))
>>> assert close_enough(x, 0), "%f is close to 0" % x
>>> assert close_enough(y, 0), "%f is close to 0" % y

>>> x, y = project(deg2rad(60), deg2rad(60), deg2rad(60), deg2rad(60))
>>> assert close_enough(x, 0), "%f is close to 0" % x
>>> assert close_enough(y, 0), "%f is close to 0" % y

>>> x, y = project(deg2rad(-60), deg2rad(-60), deg2rad(-60), deg2rad(-60))
>>> assert close_enough(x, 0), "%f is close to 0" % x
>>> assert close_enough(y, 0), "%f is close to 0" % y

>>> x, y = project(deg2rad(30), deg2rad(30), deg2rad(0), deg2rad(0))
>>> assert close_enough(x, 0.577), "%f is close to 0.577" % x
>>> assert close_enough(y, 0.666), "%f is close to 0.666" % y

>>> x, y = project(deg2rad(-30), deg2rad(-30), deg2rad(0), deg2rad(0))
>>> assert close_enough(x, -0.577), "%f is close to -0.577" % x
>>> assert close_enough(y, -0.666), "%f is close to -0.666" % y

>>> lat, lon = unproject(0, 0, deg2rad(0), deg2rad(0))
>>> assert close_enough(rad2deg(lat), 0)
>>> assert close_enough(rad2deg(lon), 0)

>>> lat, lon = unproject(0, 0, deg2rad(60), deg2rad(60))
>>> assert close_enough(rad2deg(lat), 60)
>>> assert close_enough(rad2deg(lon), 60)

>>> lat, lon = unproject(0, 0, deg2rad(-60), deg2rad(-60))
>>> assert close_enough(rad2deg(lat), -60)
>>> assert close_enough(rad2deg(lon), -60)

>>> lat, lon = deg2rad(-60), deg2rad(-60)
>>> x, y = project(lat, lon)
>>> lat_, lon_ = unproject(x, y)
>>> assert close_enough(lat_, lat), "%f is close to %f" % (lat_, lat)
>>> assert close_enough(lon_, lon), "%f is close to %f" % (lon_, lon)

>>> lat, lon = deg2rad(-60), deg2rad(0)
>>> x, y = project(lat, lon)
>>> lat_, lon_ = unproject(x, y)
>>> assert close_enough(lat_, lat), "%f is close to %f" % (lat_, lat)
>>> assert close_enough(lon_, lon), "%f is close to %f" % (lon_, lon)

>>> lat, lon = deg2rad(-60), deg2rad(60)
>>> x, y = project(lat, lon)
>>> lat_, lon_ = unproject(x, y)
>>> assert close_enough(lat_, lat), "%f is close to %f" % (lat_, lat)
>>> assert close_enough(lon_, lon), "%f is close to %f" % (lon_, lon)

>>> lat, lon = deg2rad(0), deg2rad(-60)
>>> x, y = project(lat, lon)
>>> lat_, lon_ = unproject(x, y)
>>> assert close_enough(lat_, lat), "%f is close to %f" % (lat_, lat)
>>> assert close_enough(lon_, lon), "%f is close to %f" % (lon_, lon)

>>> lat, lon = deg2rad(0), deg2rad(0)
>>> x, y = project(lat, lon)
>>> lat_, lon_ = unproject(x, y)
>>> assert close_enough(lat_, lat), "%f is close to %f" % (lat_, lat)
>>> assert close_enough(lon_, lon), "%f is close to %f" % (lon_, lon)

>>> lat, lon = deg2rad(0), deg2rad(60)
>>> x, y = project(lat, lon)
>>> lat_, lon_ = unproject(x, y)
>>> assert close_enough(lat_, lat), "%f is close to %f" % (lat_, lat)
>>> assert close_enough(lon_, lon), "%f is close to %f" % (lon_, lon)

>>> lat, lon = deg2rad(60), deg2rad(-60)
>>> x, y = project(lat, lon)
>>> lat_, lon_ = unproject(x, y)
>>> assert close_enough(lat_, lat), "%f is close to %f" % (lat_, lat)
>>> assert close_enough(lon_, lon), "%f is close to %f" % (lon_, lon)

>>> lat, lon = deg2rad(60), deg2rad(0)
>>> x, y = project(lat, lon)
>>> lat_, lon_ = unproject(x, y)
>>> assert close_enough(lat_, lat), "%f is close to %f" % (lat_, lat)
>>> assert close_enough(lon_, lon), "%f is close to %f" % (lon_, lon)

>>> lat, lon = deg2rad(60), deg2rad(60)
>>> x, y = project(lat, lon)
>>> lat_, lon_ = unproject(x, y)
>>> assert close_enough(lat_, lat), "%f is close to %f" % (lat_, lat)
>>> assert close_enough(lon_, lon), "%f is close to %f" % (lon_, lon)
"""
from math import cos, sin, asin, atan, atan2, pi, sqrt

def close_enough(a, b):
    return abs(a - b) < 0.001

def deg2rad(degrees):
    return degrees * pi / 180.0

def rad2deg(radians):
    return radians * 180.0 / pi

def project(lat, lon, lat0=0.0, lon0=0.0):
    """ Project lat, lon to x, y.
    
        Arguments given in radians.
        See: http://mathworld.wolfram.com/GnomonicProjection.html
    """
    cos_c = sin(lat0) * sin(lat) + cos(lat0) * cos(lat) * cos(lon - lon0)
    
    x = cos(lat) * sin(lon - lon0) / cos_c
    y = (cos(lat0) * sin(lat) - sin(lat0) * cos(lat) * cos(lon - lon0)) / cos_c
    
    return x, y

def unproject(x, y, lat0=0.0, lon0=0.0):
    """ Unproject x, y to lat, lon.
    
        Return values are in radians.
        See: http://mathworld.wolfram.com/GnomonicProjection.html
    """
    p = sqrt(x * x + y * y)
    c = atan(p)
    
    if p == 0.0:
        # avoid divide by zero later
        return lat0, lon0
    
    lat = asin(cos(c) * sin(lat0) + (y * sin(c) * cos(lat0)) / p)
    lon = lon0 + atan2(x * sin(c), (p * cos(lat0) * cos(c) - y * sin(lat0) * sin(c)))
    
    return lat, lon

if __name__ == '__main__':
    import doctest
    doctest.testmod()
