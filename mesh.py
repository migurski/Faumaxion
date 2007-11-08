class Vertex:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Edge:
    def __init__(self, vertexA, vertexB, triangleA, triangleB, strength):
        self.vertexA = vertexA
        self.vertexB = vertexB
        self.triangleA = triangleA
        self.triangleB = triangleB
        self.strength = strength

class Triangle:
    def __init__(self, edgeA, edgeB, edgC):
        self.edgeA = edgeA
        self.edgeB = edgeB
        self.edgeC = edgeC
