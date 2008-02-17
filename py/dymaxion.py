"""
>>> latlon2spherical(-120.0, 37.0)  #doctest: +ELLIPSIS
(0.9250..., 4.1887...)
>>> latlon2spherical(-100.0, 40.0)  #doctest: +ELLIPSIS
(0.8726..., 4.5378...)
>>> latlon2spherical(20.0, 50.0)    #doctest: +ELLIPSIS
(0.6981..., 0.3490...)
>>> latlon2spherical(120.0, -40.0)  #doctest: +ELLIPSIS
(2.2689..., 2.0943...)


>>> rs = map(deg2rad, (0.0, 60.0, 120.0, 180.0, 240.0, 300.0, 360.0))
>>> [round(r, 5) for r in rs] #doctest: +ELLIPSIS
[0.0, 1.0471..., 2.0943..., 3.1415..., 4.1887..., 5.2359..., 6.2831...]


>>> c = map(spherical2cartesian, map(deg2rad, (-90, 0, 90)), map(deg2rad, (-180, -180, -180)))
>>> [[round(a, 5) for a in xyz] for xyz in c]
[[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [-1.0, -0.0, 0.0]]

>>> c = map(spherical2cartesian, map(deg2rad, (-90, 0, 90)), map(deg2rad, (-60, -60, -60)))
>>> [[round(a, 5) for a in xyz] for xyz in c]  #doctest: +ELLIPSIS
[[-0.5, 0.8660..., 0.0], [0.0, 0.0, 1.0], [0.5, -0.8660..., 0.0]]

>>> c = map(spherical2cartesian, map(deg2rad, (-90, 0, 90)), map(deg2rad, (60, 60, 60)))
>>> [[round(a, 5) for a in xyz] for xyz in c]  #doctest: +ELLIPSIS
[[-0.5, -0.8660..., 0.0], [0.0, 0.0, 1.0], [0.5, 0.8660..., 0.0]]

>>> c = map(spherical2cartesian, map(deg2rad, (-90, 0, 90)), map(deg2rad, (180, 180, 180)))
>>> [[round(a, 5) for a in xyz] for xyz in c]
[[1.0, -0.0, 0.0], [0.0, 0.0, 1.0], [-1.0, 0.0, 0.0]]


>>> [[[round(c, 5) for c in project(lon, lat)] for lat in range(-90, 90, 30)] for lon in range(-180, 180, 30)] #doctest: +ELLIPSIS
[[[5.1019..., 1.2546...], [0.5994..., 0.0523...], [3.9437..., 0.0142...], [3.5024..., 0.0953...], [2.6182..., 0.4982...], [2.6420..., 0.9171...]], [[5.1019..., 1.2546...], [4.8404..., 0.9074...], [4.0562..., 0.3581...], [3.6768..., 0.5234...], [3.2778..., 0.6830...], [2.8571..., 0.9651...]], [[5.1019..., 1.2546...], [4.7173..., 1.0960...], [4.2943..., 0.9807...], [3.8379..., 0.9294...], [3.3932..., 1.0233...], [2.9857..., 1.1343...]], [[5.1019..., 1.2546...], [4.6875..., 1.3135...], [4.2758..., 1.3527...], [3.8568..., 1.3683...], [3.4398..., 1.3959...], [3.0198..., 1.3548]], [[5.1019..., 1.2546...], [4.7549..., 1.5133...], [4.3526..., 1.7257...], [3.8881..., 1.7842...], [2.8994..., 2.4927...], [2.9588..., 1.5559...]], [[5.1019..., 1.2546...], [4.9195..., 1.6386...], [4.7597..., 2.0206...], [3.9681..., 2.2038...], [2.5215..., 2.3855...], [2.8011..., 1.7096...]], [[5.1019..., 1.2546...], [5.1420..., 1.6809...], [5.1182..., 2.0998...], [1.9186..., 2.5482...], [2.2095..., 2.2066...], [2.4955..., 1.8443...]], [[5.1019..., 1.2546...], [5.3571..., 1.6329...], [1.2973..., 2.4489...], [1.6350..., 2.1831...], [1.9679..., 1.9372...], [2.3404..., 1.6906...]], [[5.1019..., 1.2546...], [5.4857..., 1.4636...], [0.8932..., 1.5746...], [1.3379..., 1.6685...], [1.7943..., 1.6173...], [2.2173..., 1.5020...]], [[5.1019..., 1.2546...], [0.4331..., 0.6387...], [0.9398..., 1.2020...], [1.3568..., 1.2297...], [1.7758, 1.2453...], [2.1875..., 1.2845]], [[5.1019..., 1.2546...], [5.4588..., 1.0421...], [0.9590..., 0.7263...], [1.3881..., 0.8138...], [1.8526..., 0.8722...], [2.2549..., 1.0847...]], [[5.1019..., 1.2546...], [5.3011..., 0.8884...], [1.0551..., 0.3453...], [1.4681..., 0.3942...], [2.2597..., 0.5774...], [2.4195..., 0.9594...]]]
"""
import math
from mesh import Vertex, Edge, Triangle

# Cartesian coordinates for the 12 vertices of icosahedron

vertices = { 1: Vertex( 0.420152426708710003,  0.078145249402782959,  0.904082550615019298),
             2: Vertex( 0.995009439436241649, -0.091347795276427931,  0.040147175877166645),
             3: Vertex( 0.518836730327364437,  0.835420380378235850,  0.181331837557262454),
             4: Vertex(-0.414682225320335218,  0.655962405434800777,  0.630675807891475371),
             5: Vertex(-0.515455959944041808, -0.381716898287133011,  0.767200992517747538),
             6: Vertex( 0.355781402532944713, -0.843580002466178147,  0.402234226602925571),
             7: Vertex( 0.414682225320335218, -0.655962405434800777, -0.630675807891475371),
             8: Vertex( 0.515455959944041808,  0.381716898287133011, -0.767200992517747538),
             9: Vertex(-0.355781402532944713,  0.843580002466178147, -0.402234226602925571),
            10: Vertex(-0.995009439436241649,  0.091347795276427931, -0.040147175877166645),
            11: Vertex(-0.518836730327364437, -0.835420380378235850, -0.181331837557262454),
            12: Vertex(-0.420152426708710003, -0.078145249402782959, -0.904082550615019298)}

# corners of each triangle
triangle_vertices = { 1: (vertices[1],  vertices[3],  vertices[2]),
                      2: (vertices[1],  vertices[4],  vertices[3]),
                      3: (vertices[1],  vertices[5],  vertices[4]),
                      4: (vertices[1],  vertices[6],  vertices[5]),
                      5: (vertices[1],  vertices[2],  vertices[6]),
                      6: (vertices[2],  vertices[3],  vertices[8]),
                      7: (vertices[3],  vertices[9],  vertices[8]),
                      8: (vertices[3],  vertices[4],  vertices[9]),
                      9: (vertices[4],  vertices[10], vertices[9]),
                     10: (vertices[4],  vertices[5],  vertices[10]),
                     11: (vertices[5],  vertices[11], vertices[10]),
                     12: (vertices[5],  vertices[6],  vertices[11]),
                     13: (vertices[6],  vertices[7],  vertices[11]),
                     14: (vertices[2],  vertices[7],  vertices[6]),
                     15: (vertices[2],  vertices[8],  vertices[7]),
                     16: (vertices[8],  vertices[9],  vertices[12]),
                     17: (vertices[9],  vertices[10], vertices[12]),
                     18: (vertices[10], vertices[11], vertices[12]),
                     19: (vertices[11], vertices[7],  vertices[12]),
                     20: (vertices[8],  vertices[12], vertices[7])}

# mid face coordinates
triangle_centers = {}

for tri in triangle_vertices.keys():
    v1, v2, v3 = triangle_vertices[tri]
    
    avg_x = (v1.x + v2.x + v3.x) / 3.0
    avg_y = (v1.y + v2.y + v3.y) / 3.0
    avg_z = (v1.z + v2.z + v3.z) / 3.0
    length = math.sqrt(avg_x*avg_x + avg_y*avg_y + avg_z*avg_z)

    triangle_centers[tri] = Vertex(avg_x/length, avg_y/length, avg_z/length)

# magic
_arc = 2.0 * math.asin(math.sqrt(5 - math.sqrt(5)) / math.sqrt(10))
_t = _arc / 2.0

_dve = math.sqrt(3 + math.sqrt(5)) / math.sqrt(5 + math.sqrt(5))
_el = math.sqrt(8) / math.sqrt(5 + math.sqrt(5))



def project(lon, lat):
    """ This is the main control procedure.
    """
    # Convert the given (long.,lat.) coordinate into spherical
    # polar coordinates (r, theta, phi) with radius=1.
    # Angles are given in radians, NOT degrees.
    theta, phi = latlon2spherical(lon, lat)

    # convert the spherical polar coordinates into cartesian
    # (x, y, z) coordinates.
    hx, hy, hz = spherical2cartesian(theta, phi)

    # determine which of the 20 spherical icosahedron triangles
    # the given point is in and the LCD triangle.
    tri, lcd = assign_triangle(hx, hy, hz)
    
    # Determine the corresponding Fuller map plane (x, y) point
    px, py = dymax_point(tri, lcd, hx, hy, hz)

    return px, py

def latlon2spherical(lon, lat):
    """ Convert (long., lat.) point into spherical polar coordinates with r=radius=1.
        
        Angles are given in radians.
    """
    theta_deg = 90.0 - lat
    phi_deg = lon
    if lon < 0.0:
        phi_deg = lon + 360.0

    theta = deg2rad(theta_deg)
    phi = deg2rad(phi_deg)
    
    return theta, phi

def deg2rad(degrees):
    return degrees * math.pi / 180.0

def spherical2cartesian(theta, phi):
    """ Convert spherical polar coordinates to cartesian coordinates.
    
        The angles are given in radians.
    """
    x = math.sin(theta) * math.cos(phi)
    y = math.sin(theta) * math.sin(phi)
    z = math.cos(theta)
    
    return x, y, z

def cartesian2spherical(x, y, z):
    """ Convert cartesian coordinates into spherical polar coordinates.
        
        The angles are given in radians.
    """
    if x > 0.0 and y > 0.0:
        a = deg2rad(0.0)

    if x < 0.0 and y > 0.0:
        a = deg2rad(180.0)

    if x < 0.0 and y < 0.0:
        a = deg2rad(180.0)

    if x > 0.0 and y < 0.0:
        a = deg2rad(360.0)
        
    if x == 0.0 and y > 0.0:
        phi = deg2rad(90.0)

    if x == 0.0 and y < 0.0:
        phi = deg2rad(270.0)

    if x > 0.0 and y == 0.0:
        phi = deg2rad(0.0)

    if x < 0.0 and y == 0.0:
        phi = deg2rad(180.0)

    if x != 0.0 and y != 0.0:
        phi = math.atan(y / x) + a

    theta = math.acos(z)
    
    return phi, theta

def assign_triangle(x, y, z):
    """ Determine which triangle and LCD triangle the point is in.
    """
    tri = 0
    min_distance = 9999.0
    
    # Which triangle face center is the closest to the given point
    # is the triangle in which the given point is in.
    for i in range(1, 21):
        x_diff = triangle_centers[i].x - x
        y_diff = triangle_centers[i].y - y
        z_diff = triangle_centers[i].z - z
        distance = math.sqrt(x_diff*x_diff + y_diff*y_diff + z_diff*z_diff)
        
        if distance < min_distance:
            tri = i
            min_distance = distance

    # Now the LCD triangle is determined.
    vertex1, vertex2, vertex3 = triangle_vertices[tri]

    x_diff = x - vertex1.x;
    y_diff = y - vertex1.y;
    z_diff = z - vertex1.z;
    v1_distance = math.sqrt(x_diff*x_diff + y_diff*y_diff + z_diff*z_diff);
    
    x_diff = x - vertex2.x;
    y_diff = y - vertex2.y;
    z_diff = z - vertex2.z;
    v2_distance = math.sqrt(x_diff*x_diff + y_diff*y_diff + z_diff*z_diff);
    
    x_diff = x - vertex3.x;
    y_diff = y - vertex3.y;
    z_diff = z - vertex3.z;
    v3_distance = math.sqrt(x_diff*x_diff + y_diff*y_diff + z_diff*z_diff);

    if v1_distance <= v2_distance and v2_distance <= v3_distance: lcd = 1
    if v1_distance <= v3_distance and v3_distance <= v2_distance: lcd = 6
    if v2_distance <= v1_distance and v1_distance <= v3_distance: lcd = 2
    if v2_distance <= v3_distance and v3_distance <= v1_distance: lcd = 3
    if v3_distance <= v1_distance and v1_distance <= v2_distance: lcd = 5
    if v3_distance <= v2_distance and v2_distance <= v1_distance: lcd = 4

    return tri, lcd

def dymax_point(tri, lcd, x, y, z):
    """
    """
    # In order to rotate the given point into the template spherical
    # triangle, we need the spherical polar coordinates of the center
    # of the face and one of the face vertices.
    vertex = triangle_vertices[tri][0]

    x0, y0, z0 = x, y, z
    x1, y1, z1 = vertex.x, vertex.y, vertex.z
    
    center = triangle_centers[tri]
    lon, lat = cartesian2spherical(center.x, center.y, center.z)
    
    x0, y0, z0 = axis_rotate('z', lon, x0, y0, z0)
    x1, y1, z1 = axis_rotate('z', lon, x1, y1, z1)
    
    x0, y0, z0 = axis_rotate('y', lat, x0, y0, z0)
    x1, y1, z1 = axis_rotate('y', lat, x1, y1, z1)
    
    lon, lat = cartesian2spherical(x1, y1, z1)
    lon -= deg2rad(90.0)
    
    x0, y0, z0 = axis_rotate('z', lon, x0, y0, z0)
    
    # done with these for now
    del x, y, z0, x1, y1, z1, lon, lat
    
    # exact transformation equations
    
    gz = math.sqrt(1 - x0 * x0 - y0 * y0)
    gs = math.sqrt(5 + 2 * math.sqrt(5)) / (gz * math.sqrt(15))
    
    gxp = x0 * gs
    gyp = y0 * gs
    
    ga1p = 2.0 * gyp / math.sqrt(3.0) + (_el / 3.0)
    ga2p = gxp - (gyp / math.sqrt(3)) +  (_el / 3.0)
    ga3p = (_el / 3.0) - gxp - (gyp / math.sqrt(3))
    
    ga1 = _t + math.atan((ga1p - 0.5 * _el) / _dve)
    ga2 = _t + math.atan((ga2p - 0.5 * _el) / _dve)
    ga3 = _t + math.atan((ga3p - 0.5 * _el) / _dve)
    
    gx = 0.5 * (ga2 - ga3)
    gy = (1.0 / (2.0 * math.sqrt(3))) * (2 * ga1 - ga2 - ga3)
    
    # Re-scale so plane triangle edge length is 1.
    x, y = gx/_arc, gy/_arc

    # rotate and translate to correct position
    return transform_triangle(tri, lcd, x, y)
    
def transform_triangle(tri, lcd, x, y):
    """ Given a triangle and a projected point, transform point
        to its proper position in a default map configuration.
    """
    if tri == 1:
        x, y = plane_rotate(240.0, x, y)
        tx = x + 2.0
        ty = y + 7.0 / (2.0 * math.sqrt(3.0))

    elif tri == 2:
        x, y = plane_rotate(300.0, x, y)
        tx = x + 2.0
        ty = y + 5.0 / (2.0 * math.sqrt(3.0))

    elif tri == 3:
        x, y = plane_rotate(0.0, x, y)
        tx = x + 2.5
        ty = y + 2.0 / math.sqrt(3.0)

    elif tri == 4:
        x, y = plane_rotate(60.0, x, y)
        tx = x + 3.0
        ty = y + 5.0 / (2.0 * math.sqrt(3.0))

    elif tri == 5:
        x, y = plane_rotate(180.0, x, y)
        tx = x + 2.5
        ty = y + 4.0 * math.sqrt(3.0) / 3.0

    elif tri == 6:
        x, y = plane_rotate(300.0, x, y)
        tx = x + 1.5
        ty = y + 4.0 * math.sqrt(3.0) / 3.0

    elif tri == 7:
        x, y = plane_rotate(300.0, x, y)
        tx = x + 1.0
        ty = y + 5.0 / (2.0 * math.sqrt(3.0))

    elif tri == 8:
        x, y = plane_rotate(0.0, x, y)
        tx = x + 1.5
        ty = y + 2.0 / math.sqrt(3.0)

    elif tri == 9:
        if lcd > 2:
            x, y = plane_rotate(300.0, x, y)
            tx = x + 1.5
            ty = y + 1.0 / math.sqrt(3.0)
        else:
            x, y = plane_rotate(0.0, x, y)
            tx = x + 2.0
            ty = y + 1.0 / (2.0 * math.sqrt(3.0))

    elif tri == 10:
        x, y = plane_rotate(60.0, x, y)
        tx = x + 2.5
        ty = y + 1.0 / math.sqrt(3.0)

    elif tri == 11:
        x, y = plane_rotate(60.0, x, y)
        tx = x + 3.5
        ty = y + 1.0 / math.sqrt(3.0)

    elif tri == 12:
        x, y = plane_rotate(120.0, x, y)
        tx = x + 3.5
        ty = y + 2.0 / math.sqrt(3.0)

    elif tri == 13:
        x, y = plane_rotate(60.0, x, y)
        tx = x + 4.0
        ty = y + 5.0 / (2.0 * math.sqrt(3.0))

    elif tri == 14:
        x, y = plane_rotate(0.0, x, y)
        tx = x + 4.0
        ty = y + 7.0 / (2.0 * math.sqrt(3.0)) 

    elif tri == 15:
        x, y = plane_rotate(0.0, x, y)
        tx = x + 5.0
        ty = y + 7.0 / (2.0 * math.sqrt(3.0)) 

    elif tri == 16:
        if lcd < 4:
            x, y = plane_rotate(60.0, x, y)
            tx = x + 0.5
            ty = y + 1.0 / math.sqrt(3.0)
        else:
            x, y = plane_rotate(0.0, x, y)
            tx = x + 5.5
            ty = y + 2.0 / math.sqrt(3.0)

    elif tri == 17:
        x, y = plane_rotate(0.0, x, y)
        tx = x + 1.0
        ty = y + 1.0 / (2.0 * math.sqrt(3.0))

    elif tri == 18:
        x, y = plane_rotate(120.0, x, y)
        tx = x + 4.0
        ty = y + 1.0 / (2.0 * math.sqrt(3.0))

    elif tri == 19:
        x, y = plane_rotate(120.0, x, y)
        tx = x + 4.5
        ty = y + 2.0 / math.sqrt(3.0)

    elif tri == 20:
        x, y = plane_rotate(300.0, x, y)
        tx = x + 5.0
        ty = y + 5.0 / (2.0 * math.sqrt(3.0))

    else:
        raise Exception('Unknown triangle: %d' % tri)

    return tx, ty

def plane_rotate(angle, x, y):
    """ Rotate the point to correct orientation in XY-plane.
    
        Angle is given in degrees.
    """
    theta, x_, y_ = deg2rad(angle), x, y
    x = x_ * math.cos(theta) - y_ * math.sin(theta)
    y = x_ * math.sin(theta) + y_ * math.cos(theta)
    
    return x, y

def axis_rotate(axis, theta, x, y, z):
    """ Rotate a 3-D point about the specified axis.
    
        Theta is given in radians.
    """
    x_, y_, z_ = x, y, z
    
    if axis == 'x':
        y = y_ * math.cos(theta) + z_ * math.sin(theta)
        z = z_ * math.cos(theta) - y_ * math.sin(theta)
    
    if axis == 'y':
        x = x_ * math.cos(theta) - z_ * math.sin(theta)
        z = x_ * math.sin(theta) + z_ * math.cos(theta)
    
    if axis == 'z':
        x = x_ * math.cos(theta) + y_ * math.sin(theta)
        y = y_ * math.cos(theta) - x_ * math.sin(theta)

    return x, y, z



if __name__ == '__main__':
    import doctest
    doctest.testmod()
