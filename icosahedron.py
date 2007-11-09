"""
"""
import math, mesh

class Face(mesh.Triangle):
    # TODO: write me
    pass

# Cartesian coordinates for the 12 vertices of icosahedron
vertices = { 1: mesh.Vertex( 0.420152426708710003,  0.078145249402782959,  0.904082550615019298),
             2: mesh.Vertex( 0.995009439436241649, -0.091347795276427931,  0.040147175877166645),
             3: mesh.Vertex( 0.518836730327364437,  0.835420380378235850,  0.181331837557262454),
             4: mesh.Vertex(-0.414682225320335218,  0.655962405434800777,  0.630675807891475371),
             5: mesh.Vertex(-0.515455959944041808, -0.381716898287133011,  0.767200992517747538),
             6: mesh.Vertex( 0.355781402532944713, -0.843580002466178147,  0.402234226602925571),
             7: mesh.Vertex( 0.414682225320335218, -0.655962405434800777, -0.630675807891475371),
             8: mesh.Vertex( 0.515455959944041808,  0.381716898287133011, -0.767200992517747538),
             9: mesh.Vertex(-0.355781402532944713,  0.843580002466178147, -0.402234226602925571),
            10: mesh.Vertex(-0.995009439436241649,  0.091347795276427931, -0.040147175877166645),
            11: mesh.Vertex(-0.518836730327364437, -0.835420380378235850, -0.181331837557262454),
            12: mesh.Vertex(-0.420152426708710003, -0.078145249402782959, -0.904082550615019298)}

# Edges and Triangles
edges = []
triangles = {}

for t, v1, v2 in [(1, 1, 3), (1, 3, 2), (1, 2, 1), (2, 1, 4), (2, 4, 3), (2, 3, 1), (3, 1, 5), (3, 5, 4), (3, 4, 1), (4, 1, 6), (4, 6, 5), (4, 5, 1), (5, 1, 2), (5, 2, 6), (5, 6, 1), (6, 2, 3), (6, 3, 8), (6, 8, 2), (7, 3, 9), (7, 9, 8), (7, 8, 3), (8, 3, 4), (8, 4, 9), (8, 9, 3), (9, 4, 10), (9, 10, 9), (9, 9, 4), (10, 4, 5), (10, 5, 10), (10, 10, 4), (11, 5, 11), (11, 11, 10), (11, 10, 5), (12, 5, 6), (12, 6, 11), (12, 11, 5), (13, 6, 7), (13, 7, 11), (13, 11, 6), (14, 2, 7), (14, 7, 6), (14, 6, 2), (15, 2, 8), (15, 8, 7), (15, 7, 2), (16, 8, 9), (16, 9, 12), (16, 12, 8), (17, 9, 10), (17, 10, 12), (17, 12, 9), (18, 10, 11), (18, 11, 12), (18, 12, 10), (19, 11, 7), (19, 7, 12), (19, 12, 11), (20, 8, 12), (20, 12, 7), (20, 7, 8)]:
    
    # assign a triangle
    if triangles.has_key(t):
        triangle = triangles[t]
    else:
        triangle = triangles[t] = mesh.Triangle(None, None, None)

    # this edge has two vertices
    vertexA = vertices[v1]
    vertexB = vertices[v2]
    
    # see if the edge already exists in the opposite direction
    edge = False
    for e in edges:
        if e.vertexB is vertexA and e.vertexA is vertexB:
            edge = e
            break
    
    if edge:
        # edge exists, so assign it the appropriate triangle
        edge.triangleB = triangle
    else:
        # new edge, just one triangle for now
        edge = mesh.Edge(vertexA, vertexB, triangle, None, 1)

    if triangle.edgeA is None:
        triangle.edgeA = edge
    
    elif triangle.edgeB is None:
        triangle.edgeB = edge
    
    elif triangle.edgeC is None:
        triangle.edgeC = edge

def deg2rad(degrees):
    return degrees * math.pi / 180.0

def rad2deg(radians):
    return radians * 180.0 / math.pi

def latlon2spherical(lat, lon):
    """ Convert (lat, lon) point to spherical polar coordinates.
        
        (lat, lon) is given in degrees, (theta, phi) is returned in radians
    """
    if lon < 0:
        lon += 360.0

    return deg2rad(90.0 - lat), deg2rad(lon)

def spherical2latlon(theta, phi):
    """ Convert spherical polar coordinates to (lat, lon) point.
        
        (theta, phi) is given in radians, (lat, lon) is returned in degrees.
    """
    return 90.0 - rad2deg(theta), rad2deg(phi)

def spherical2vertex(theta, phi):
    """ Convert spherical polar coordinates to vertex.
    
        (theta, phi) is given in radians.
    """
    x = math.sin(theta) * math.cos(phi)
    y = math.sin(theta) * math.sin(phi)
    z = math.cos(theta)
    
    return mesh.Vertex(x, y, z)

def vertex2spherical(vertex):
    """ Convert vertex to spherical polar coordinates.
        
        (theta, phi) is returned in radians.
    """
    if vertex.x > 0.0 and vertex.y > 0.0:
        a = deg2rad(0.0)

    if vertex.x < 0.0 and vertex.y > 0.0:
        a = deg2rad(180.0)

    if vertex.x < 0.0 and vertex.y < 0.0:
        a = deg2rad(180.0)

    if vertex.x > 0.0 and vertex.y < 0.0:
        a = deg2rad(360.0)
        
    if vertex.x == 0.0 and vertex.y > 0.0:
        phi = deg2rad(90.0)

    if vertex.x == 0.0 and vertex.y < 0.0:
        phi = deg2rad(270.0)

    if vertex.x > 0.0 and vertex.y == 0.0:
        phi = deg2rad(0.0)

    if vertex.x < 0.0 and vertex.y == 0.0:
        phi = deg2rad(180.0)

    if vertex.x != 0.0 and vertex.y != 0.0:
        phi = math.atan(vertex.y / vertex.x) + a

    theta = math.acos(vertex.z)
    
    return theta, phi

def vertex2triangle(vertex):
    """ Determine which triangle the point is in.
    
        Return Triangle object.
    """
    distances = [(vertex.distance(triangle.center()), triangle) for triangle in triangles.values()]
    distances.sort()
    
    triangle = distances[0][1]
    
    # short circuit for now
    return triangle
    
    # Now the LCD triangle is determined.
    v1_distance, v2_distance, v3_distance = [vertex.distance(v) for v in triangle.vertices()]

    if v1_distance <= v2_distance and v2_distance <= v3_distance: lcd = 1
    if v1_distance <= v3_distance and v3_distance <= v2_distance: lcd = 6
    if v2_distance <= v1_distance and v1_distance <= v3_distance: lcd = 2
    if v2_distance <= v3_distance and v3_distance <= v1_distance: lcd = 3
    if v3_distance <= v1_distance and v1_distance <= v2_distance: lcd = 5
    if v3_distance <= v2_distance and v2_distance <= v1_distance: lcd = 4

    return triangle, lcd



if __name__ == '__main__':
    import doctest
    doctest.testmod()
