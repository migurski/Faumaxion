import math

class Vertex:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return 'Vertex(%(x).3f, %(y).3f, %(z).3f)' % self.__dict__

    def distance(self, other):
        """ Return distance from this vertex to another.
        """
        diff = Vertex(other.x - self.x, other.y - self.y, other.z - self.z)
        return math.sqrt(diff.x * diff.x + diff.y * diff.y + diff.z * diff.z)

class Edge:
    def __init__(self, vertexA, vertexB, triangleA, triangleB, strength):
        self.vertexA = vertexA
        self.vertexB = vertexB
        self.triangleA = triangleA
        self.triangleB = triangleB
        self.strength = strength

    def triangles(self):
        return (self.triangleA, self.triangleB)

class Triangle:
    def __init__(self, edgeA, edgeB, edgeC):
        self.edgeA = edgeA
        self.edgeB = edgeB
        self.edgeC = edgeC
        self._center = False

    def center(self):
        if not self._center:
            v1, v2, v3 = self.vertices()
            
            avg_x = (v1.x + v2.x + v3.x) / 3.0
            avg_y = (v1.y + v2.y + v3.y) / 3.0
            avg_z = (v1.z + v2.z + v3.z) / 3.0
    
            length = math.sqrt(avg_x*avg_x + avg_y*avg_y + avg_z*avg_z)
            self._center = Vertex(avg_x/length, avg_y/length, avg_z/length)

        return self._center
            
    def edges(self):
        return (self.edgeA, self.edgeB, self.edgeC)
    
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
