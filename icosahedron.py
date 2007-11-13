"""
"""
import math, mesh, gnomonic, transform

# constants used to arrange faces
LAND = 'contiguous land masses'
WATER = 'contiguous bodies of water'

class Face(mesh.Triangle):
    """ A Triangle with some methods specific to this icosahedron.
    """
    def __init__(self, edgeA, edgeB, edgeC):
        mesh.Triangle.__init__(self, edgeA, edgeB, edgeC)
        
        self.transform = transform.Transformation(1/average_edge_length, 0, 0,
                                                  0, -1/average_edge_length, 0)
        
    def center_latlon(self):
        """ Return lat, lon of center in degrees.
        """
        return vertex2latlon(self.center())

    def project_vertex(self, vertex):
        """ Return x, y position of projected vertex on this face.
        """
        lat, lon = vertex2latlon(vertex)
        
        return self.project_latlon(lat, lon)

    def project_latlon(self, lat, lon):
        """ Return x, y position of projected lat, lon on this face.
        
            Arguments given in degrees.
        """
        lat0, lon0 = self.center_latlon()
        
        x, y = gnomonic.project(*map(gnomonic.deg2rad, (lat, lon, lat0, lon0)))
        
        return self.transform.apply(x, y)
        
    def adjoin(self, other):
        """ Adjoins another face to this one, if they share an edge.
        
            Works by modifying the transform property of the other edge.
        """
        edge = self.shared(other)

        # 2D positions of vertices in other projection
        a1x, a1y = other.project_vertex(edge.vertexA)
        b1x, b1y = other.project_vertex(edge.vertexB)
        c1x, c1y = derive_third_point(a1x, a1y, b1x, b1y)
        
        # 2D positions of vertices in this projection
        a2x, a2y = self.project_vertex(edge.vertexA)
        b2x, b2y = self.project_vertex(edge.vertexB)
        c2x, c2y = derive_third_point(a2x, a2y, b2x, b2y)
        
        t = transform.deriveTransformation(a1x, a1y, a2x, a2y, b1x, b1y, b2x, b2y, c1x, c1y, c2x, c2y)
        other.transform = other.transform.multiply(t)

    def arrange_neighbors(self, preferred_kind=LAND):
        """ Adjoin all neighbors to this face into a single map.
        """
        seen = []
        remain = [(None, self, [])]
        
        if preferred_kind == LAND:
            kind_weights = {LAND: 0, WATER: 2}
        elif preferred_kind == WATER:
            kind_weights = {WATER: 0, LAND: 2}
        else:
            raise Exception("I don't know the kind '%s'" % preferred_kind)
        
        while len(remain):
            # do a breadth-first traversal of all neighboring faces
            remain.sort()
            kind, face, chain = remain.pop(0)
            
            if face in seen:
                continue
            else:
                seen.append(face)
        
            if len(chain):
                chain[-1].adjoin(face)
            
            chain = chain[:] + [face]
            
            for neighbor in face.neighbors():
                edge = face.shared(neighbor)
                remain.append((kind_weights[edge.kind] + len(chain), neighbor, chain))

    def orient_north(self, lat, lon):
        """ Transform this face so that (lat, lon) is locally north = up.
        """
        x1, y1 = self.project_latlon(lat, lon)
        x2, y2 = self.project_latlon(lat+1, lon)

        # -90 deg is the desired rotation
        theta = math.atan2(y2 - y1, x2 - x1)
        diff = deg2rad(-90) - theta
        
        t = transform.Transformation(math.cos(diff), -math.sin(diff), 0, math.sin(diff), math.cos(diff), 0)
        self.transform = self.transform.multiply(t)

def deg2rad(degrees):
    return degrees * math.pi / 180.0

def rad2deg(radians):
    return radians * 180.0 / math.pi

def latlon2vertex(lat, lon):
    """ Convert (lat, lon) point to vertex.
        
        (lat, lon) is given in degrees.
    """
    if lon < 0:
        lon += 360.0

    theta, phi = deg2rad(90.0 - lat), deg2rad(lon)

    x = math.sin(theta) * math.cos(phi)
    y = math.sin(theta) * math.sin(phi)
    z = math.cos(theta)
    
    vertex = mesh.Vertex(x, y, z)
    return vertex

def vertex2latlon(vertex):
    """ Convert vertex to (lat, lon) point.
        
        (lat, lon) is returned in degrees.
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
    lat, lon = 90.0 - rad2deg(theta), rad2deg(phi)
    return lat, lon

def vertex2face(vertex):
    """ Determine which face the point is in.
    
        Return Face object.
    """
    distances = [(vertex.distance(face.center()), face) for face in faces.values()]
    distances.sort()
    
    face = distances[0][1]
    
    # short circuit for now, maybe do the lcd later
    return face
    
    # Now the LCD triangle is determined.
    v1_distance, v2_distance, v3_distance = [vertex.distance(v) for v in face.vertices()]

    if v1_distance <= v2_distance and v2_distance <= v3_distance: lcd = 1
    if v1_distance <= v3_distance and v3_distance <= v2_distance: lcd = 6
    if v2_distance <= v1_distance and v1_distance <= v3_distance: lcd = 2
    if v2_distance <= v3_distance and v3_distance <= v1_distance: lcd = 3
    if v3_distance <= v1_distance and v1_distance <= v2_distance: lcd = 5
    if v3_distance <= v2_distance and v2_distance <= v1_distance: lcd = 4

    return face, lcd

def derive_third_point(p1x, p1y, p2x, p2y):
    """ Return a third (x, y) point for two given points.
    
        Given two points, return a third point that forms an equilateral
        right triangle, if the line between the two given points is the
        hypotenuse. There's no particular reason this triangle has to be
        right or equilateral - it just needs to be predictable,
        congruent, and easy to eyeball for correctness.
        
        See http://mike.teczno.com/notes/two-fingers.html
    """
    # a vector from a to b
    p3x, p3y = p2x - p1x, p2y - p1y
    theta = math.atan2(p3y, p3x)
    
    # two more unit-length vectors, one for each leg of the equilateral right triangle
    leg1x, leg1y = math.cos(theta + math.pi/4), math.sin(theta + math.pi/4)
    leg2x, leg2y = math.cos(theta + 3*math.pi/4), math.sin(theta + 3*math.pi/4)
    
    # slope and intercept for each line
    # intercept derived from http://mathworld.wolfram.com/Line.html (2)
    slope1 = leg1y / leg1x
    intercept1 = p1y - slope1 * p1x

    slope2 = leg2y / leg2x
    intercept2 = p2y - slope2 * p2x
    
    # solve for x and y of the third point
    p3x = (intercept2 - intercept1) / (slope1 - slope2)
    p3y = slope1 * p3x + intercept1
    
    return p3x, p3y

# Refers to the projected, two-dimensional length
average_edge_length = 1.323169076499213670

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

# Edges and Faces
edges = {}
faces = {}

edge_kinds = {(1, 2): LAND, (2, 3): LAND, (1, 3): LAND,
              (1, 4): LAND, (3, 4): LAND,
              (1, 5): LAND, (4, 5): LAND,
              (1, 6): WATER, (5, 6): LAND,
              (2, 6): WATER,
              (2, 8): WATER, (3, 8): WATER,
              (3, 9): WATER, (8, 9): WATER,
              (4, 9): LAND,
              (4, 10): LAND, (9, 10): LAND,
              (5, 10): WATER,
              (5, 11): WATER, (10, 11): WATER,
              (6, 11): LAND,
              (6, 7): LAND, (7, 11): LAND,
              (2, 7): WATER,
              (7, 8): WATER,
              (8, 12): LAND, (9, 12): LAND,
              (10, 12): WATER,
              (11, 12): WATER, 
              (7, 12): WATER}

for t, v1, v2 in [(1, 1, 3), (1, 3, 2), (1, 2, 1), (2, 1, 4), (2, 4, 3), (2, 3, 1), (3, 1, 5), (3, 5, 4), (3, 4, 1), (4, 1, 6), (4, 6, 5), (4, 5, 1), (5, 1, 2), (5, 2, 6), (5, 6, 1), (6, 2, 3), (6, 3, 8), (6, 8, 2), (7, 3, 9), (7, 9, 8), (7, 8, 3), (8, 3, 4), (8, 4, 9), (8, 9, 3), (9, 4, 10), (9, 10, 9), (9, 9, 4), (10, 4, 5), (10, 5, 10), (10, 10, 4), (11, 5, 11), (11, 11, 10), (11, 10, 5), (12, 5, 6), (12, 6, 11), (12, 11, 5), (13, 6, 7), (13, 7, 11), (13, 11, 6), (14, 2, 7), (14, 7, 6), (14, 6, 2), (15, 2, 8), (15, 8, 7), (15, 7, 2), (16, 8, 9), (16, 9, 12), (16, 12, 8), (17, 9, 10), (17, 10, 12), (17, 12, 9), (18, 10, 11), (18, 11, 12), (18, 12, 10), (19, 11, 7), (19, 7, 12), (19, 12, 11), (20, 8, 12), (20, 12, 7), (20, 7, 8)]:
    
    # assign a face
    if faces.has_key(t):
        face = faces[t]
    else:
        face = faces[t] = Face(None, None, None)

    edge_key = (min(v1, v2), max(v1, v2))
    
    # this edge has two vertices
    vertexA = vertices[v1]
    vertexB = vertices[v2]
    
    # see if the edge already exists in the opposite direction
    try:
        edge = edges[edge_key]
    except KeyError:
        edge = False
    
    if edge:
        # edge exists, so assign it the appropriate face
        edge.triangleB = face
    else:
        # new edge, just one face for now
        kind = edge_kinds[edge_key]
        edge = mesh.Edge(vertexA, vertexB, face, None, kind)
        edges[edge_key] = edge

    if face.edgeA is None:
        face.edgeA = edge
    
    elif face.edgeB is None:
        face.edgeB = edge
    
    elif face.edgeC is None:
        face.edgeC = edge

del edge_kinds



if __name__ == '__main__':
    import doctest
    doctest.testmod()
