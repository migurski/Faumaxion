import sys, gzip, re
import gnomonic, icosahedron, mesh
import PIL.Image as Image
from PIL.ImageDraw import ImageDraw

min_x, min_y, max_x, max_y = 9999, 9999, -9999, -9999

points = []
img = Image.new('RGB', (800, 400), 0x00)
draw = ImageDraw(img)

re_intersections = re.compile(r'^(-?\d*[02468]), (-?\d*[02468]): #\w{6} \((\d+), (\d+), (\d+)\)')

for line in gzip.open('world.topo.bathy-colors.txt.gz'):
    intersection = re_intersections.match(line)

    if intersection:
        lat, lon, r, g, b = [int(intersection.group(i)) for i in (1, 2, 3, 4, 5)]
        
        # Convert the given (long.,lat.) coordinate into spherical
        # polar coordinates (r, theta, phi) with radius=1.
        # Angles are given in radians, NOT degrees.
        theta, phi = icosahedron.latlon2spherical(lat, lon)
    
        # convert the spherical polar coordinates into cartesian
        # (x, y, z) coordinates.
        vertex = icosahedron.spherical2vertex(theta, phi)
    
        # determine which of the 20 spherical icosahedron triangles
        # the given point is in and the LCD triangle.
        triangle = icosahedron.vertex2triangle(vertex)
        
        # Determine the corresponding Fuller map plane (x, y) point
        theta, phi = icosahedron.vertex2spherical(triangle.center())
        lat0, lon0 = icosahedron.spherical2latlon(theta, phi)
        
        x, y = gnomonic.project(*map(gnomonic.deg2rad, (lat, lon, lat0, lon0)))
        
        min_x, min_y = min(x, min_x), min(y, min_y)
        max_x, max_y = max(x, max_x), max(y, max_y)

        points.append((x, y, lat, lon, (r, g, b)))

print (min_x, min_y), (max_x, max_y)

top, left, bottom, right = 10, 10, img.size[1] - 10, img.size[0] - 10

mx = (right - left) / (max_x - min_x)
my = (bottom - top) / (max_y - min_y)

mx, my = min(mx, my), min(mx, my)

bx = left - mx * min_x
by = top - my * min_y


for (x, y, lat, lon, color) in points:
    x, y = mx * x + bx, my * y + by
    draw.rectangle((x-1, y-1, x, y), fill=color)

img.save('out.png')