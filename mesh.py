import math

class Vertex:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return 'Vertex(%(x).3f, %(y).3f, %(z).3f)' % self.__dict__
        
    def clone(self):
        return Vertex(self.x, self.y, self.z)

    def distance(self, other):
        """ Return distance from this vertex to another.
        """
        diff = Vertex(other.x - self.x, other.y - self.y, other.z - self.z)
        return math.sqrt(diff.x * diff.x + diff.y * diff.y + diff.z * diff.z)

    def midpoint(self, other):
        """ Return a new vertex betweem this and another.
        """
        return Vertex(.5 * (self.x + other.x), .5 * (self.y + other.y), .5 * (self.z + other.z))

class Edge:
    def __init__(self, vertexA, vertexB, triangleA, triangleB, kind):
        self.vertexA = vertexA
        self.vertexB = vertexB
        self.triangleA = triangleA
        self.triangleB = triangleB
        self.kind = kind

    def triangles(self):
        return (self.triangleA, self.triangleB)
        
    def matches(self, other):
        """ Returns true if this edge and the other share the same two vertices.
        """
        if self.vertexA is other.vertexA and self.vertexB is other.vertexB:
            # same edge
            return True

        elif self.vertexA is other.vertexB and self.vertexB is other.vertexA:
            # same vertices, but reversed
            return True
            
        else:
            # not the same vertices at all
            return False

class Triangle:
    def __init__(self, edgeA, edgeB, edgeC):
        self.edgeA = edgeA
        self.edgeB = edgeB
        self.edgeC = edgeC
        self.center = None
        self.calculate_center()

    def calculate_center(self):
        try:
            v1, v2, v3 = self.vertices()
            
            avg_x = (v1.x + v2.x + v3.x) / 3.0
            avg_y = (v1.y + v2.y + v3.y) / 3.0
            avg_z = (v1.z + v2.z + v3.z) / 3.0
    
            length = math.sqrt(avg_x*avg_x + avg_y*avg_y + avg_z*avg_z)
            self.center = Vertex(avg_x/length, avg_y/length, avg_z/length)

        except AttributeError:
            self.center = None
            
    def edges(self):
        return (self.edgeA, self.edgeB, self.edgeC)
    
    def shared(self, other):
        """ Return shared edge.
        """
        for selfEdge in self.edges():
            for otherEdge in other.edges():
                if selfEdge.matches(otherEdge):
                    return selfEdge

        raise Exception("Sorry, those two faces don't seem to touch")
    
    def neighbors(self):
        """ Return neighboring triangles, in order.
        """
        neighbors = []
        
        for edge in self.edges():
            for neighbor in edge.triangles():
                if neighbor is not self:
                    neighbors.append(neighbor)

        return neighbors

    def vertices(self):
        """ Return three vertices, in order.
        """
        eAvA = self.edgeA.vertexA
        eAvB = self.edgeA.vertexB
        eBvA = self.edgeB.vertexA
        eBvB = self.edgeB.vertexB
        eCvA = self.edgeC.vertexA
        eCvB = self.edgeC.vertexB
        
        if eAvB is eBvA:
            v1, v2 = eAvA, eBvA
        elif eAvB is eBvB:
            v1, v2 = eAvA, eBvB
        elif eAvA is eBvA:
            v1, v2 = eAvB, eBvA
        elif eAvA is eBvB:
            v1, v2 = eAvB, eBvB
        
        if eBvB is eCvA:
            v2, v3 = eBvA, eCvA
        elif eBvB is eCvB:
            v2, v3 = eBvA, eCvB
        elif eBvA is eCvA:
            v2, v3 = eBvB, eCvA
        elif eBvA is eCvB:
            v2, v3 = eBvB, eCvB

        return v1, v2, v3
