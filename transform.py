"""
>>> t = Transformation(1, 0, 0, 0, 1, 0)
>>> t.apply(3, 3)
(3.0, 3.0)

>>> t = Transformation(-1, 0, 0, 0, -1, 0)
>>> t.apply(3, 3)
(-3.0, -3.0)

>>> t = Transformation(0, 1, 0, 1, 0, 0)
>>> t.apply(1, 2)
(2.0, 1.0)

>>> t = Transformation(0, -1, 0, -1, 0, 0)
>>> t.apply(1, 2)
(-2.0, -1.0)

>>> d = [(1, 1), (2, 2), (-2, 4), (4, -5), (3, -3), (4, 4)]
>>> t1 = Transformation(-2, -1, 0, 1, 2, 3)
>>> t2 = Transformation(3, 4, 5, 6, 7, 8)

>>> [t1.unapply(*t1.apply(x, y)) for (x, y) in d]
[(1.0, 1.0), (2.0, 2.0), (-2.0, 4.0), (4.0, -5.0), (3.0, -3.0), (4.0, 4.0)]
>>> [t2.unapply(*t2.apply(x, y)) for (x, y) in d]
[(1.0, 1.0), (2.0, 2.0), (-2.0, 4.0), (4.0, -5.0), (3.0, -3.0), (4.0, 4.0)]

>>> t3 = t1.multiply(t2)
>>> [t3.apply(x, y) == t2.apply(*t1.apply(x, y)) for (x, y) in d]
[True, True, True, True, True, True]
>>> [t3.unapply(*t3.apply(x, y)) for (x, y) in d]
[(1.0, 1.0), (2.0, 2.0), (-2.0, 4.0), (4.0, -5.0), (3.0, -3.0), (4.0, 4.0)]

>>> t = deriveTransformation(1, 1, 2, 2, 3, 4, 4, 3, 5, 5, -5, -5)
>>> t.apply(1, 1)
(2.0, 2.0)
>>> t.apply(3, 4)
(4.0, 3.0)
>>> t.apply(5, 5)
(-5.0, -5.0)
"""

class Transformation:

    def __init__(self, ax, bx, cx, ay, by, cy):
        self.ax = float(ax)
        self.bx = float(bx)
        self.cx = float(cx)
        self.ay = float(ay)
        self.by = float(by)
        self.cy = float(cy)

    def data(self):
        return (self.ax, self.bx, self.cx, self.ay, self.by, self.cy)
        
    def clone(self):
        return Transformation(*self.data())
    
    def apply(self, x, y):
        return (self.ax * x + self.bx * y + self.cx), \
               (self.ay * x + self.by * y + self.cy)

    def unapply(self, x, y):
	    return (x * self.by - y * self.bx - self.cx * self.by + self.cy * self.bx) / (self.ax * self.by - self.ay * self.bx), \
	           (x * self.ay - y * self.ax - self.cx * self.ay + self.cy * self.ax) / (self.bx * self.ay - self.by * self.ax)

    def multiply(self, other):
        ax = (other.ax * self.ax + other.bx * self.ay)
        bx = (other.ax * self.bx + other.bx * self.by)
        cx = (other.ax * self.cx + other.bx * self.cy + other.cx)

        ay = (other.ay * self.ax + other.by * self.ay)
        by = (other.ay * self.bx + other.by * self.by)
        cy = (other.ay * self.cx + other.by * self.cy + other.cy)
        
        return Transformation(ax, bx, cx, ay, by, cy)

def deriveTransformation(a1x, a1y, a2x, a2y, b1x, b1y, b2x, b2y, c1x, c1y, c2x, c2y):
    """ Generates a transform based on three pairs of points, a1 -> a2, b1 -> b2, c1 -> c2.
    """
    ax, bx, cx = linearSolution(a1x, a1y, a2x, b1x, b1y, b2x, c1x, c1y, c2x)
    ay, by, cy = linearSolution(a1x, a1y, a2y, b1x, b1y, b2y, c1x, c1y, c2y)
    
    return Transformation(ax, bx, cx, ay, by, cy)

def linearSolution(r1, s1, t1, r2, s2, t2, r3, s3, t3):
    """ Solves a system of linear equations.

          t1 = (a * r1) + (b + s1) + c
          t2 = (a * r2) + (b + s2) + c
          t3 = (a * r3) + (b + s3) + c

        r1 - t3 are the known values.
        a, b, c are the unknowns to be solved.
        returns the a, b, c coefficients.
    """

    # make them all floats
    r1, s1, t1, r2, s2, t2, r3, s3, t3 = map(float, (r1, s1, t1, r2, s2, t2, r3, s3, t3))

    a = (((t2 - t3) * (s1 - s2)) - ((t1 - t2) * (s2 - s3))) \
      / (((r2 - r3) * (s1 - s2)) - ((r1 - r2) * (s2 - s3)))

    b = (((t2 - t3) * (r1 - r2)) - ((t1 - t2) * (r2 - r3))) \
      / (((s2 - s3) * (r1 - r2)) - ((s1 - s2) * (r2 - r3)))

    c = t1 - (r1 * a) - (s1 * b)
    
    return a, b, c

if __name__ == '__main__':
    import doctest
    doctest.testmod()