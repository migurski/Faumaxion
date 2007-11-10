import sys, gzip, re, random, math, cPickle
import gnomonic, icosahedron, mesh
import PIL.Image as Image
from PIL.ImageDraw import ImageDraw

# seen = []
# remain = [(random.choice(icosahedron.faces.values()), [])]
# 
# while len(remain):
#     face, chain = remain.pop(0)
#     
#     if face in seen:
#         continue
#     else:
#         seen.append(face)
# 
#     print 'Face', id(face), 'seen', len(seen), 'chain', map(id, chain)
#     
#     for vertex in face.vertices():
#         print vertex, face.project_vertex(vertex)
#     
#     chain = chain[:] + [face]
#     
#     for neighbor in face.neighbors():
#         remain.append((neighbor, chain))

points = []
img = Image.new('RGB', (600, 600), 0x00)
draw = ImageDraw(img)

re_intersections = re.compile(r'^(-?\d*[05]), (-?\d*[05]): #\w{6} \((\d+), (\d+), (\d+)\)')
re_intersections = re.compile(r'^(-?\d*[02468]), (-?\d*[02468]): #\w{6} \((\d+), (\d+), (\d+)\)')
re_intersections = re.compile(r'^(-?\d*[\d]), (-?\d*[\d]): #\w{6} \((\d+), (\d+), (\d+)\)')

print 'Loading colors...'
colors = cPickle.load(gzip.open('world.topo.bathy-colors.pickle.gz'))

print 'Projecting points...'
for lat in range(-90, 90, 2):
    for lon in range(-180, 180, 2):
        try:
            r, g, b = colors[lat, lon]
        except KeyError:
            continue

        # Convert the given (long.,lat.) coordinate into spherical
        # polar coordinates (r, theta, phi) with radius=1.
        # Angles are given in radians, NOT degrees.
        theta, phi = icosahedron.latlon2spherical(lat, lon)
        
        # convert the spherical polar coordinates into cartesian
        # (x, y, z) coordinates.
        vertex = icosahedron.spherical2vertex(theta, phi)
        
        # determine which of the 20 spherical icosahedron faces
        # the given point is in and the LCD face.
        face = icosahedron.vertex2face(vertex)
        
        x, y = face.project_latlon(lat, lon)
        
        #for f, other in icosahedron.faces.items():
        #    if other is face:
        #        f -= 1
        #        
        #        x += (f % 7)
        #        y += math.floor(f / 7.0)

        points.append((x, y, lat, lon, (r, g, b)))

min_x = min([x for (x, y, lat, lon, color) in points])
min_y = min([y for (x, y, lat, lon, color) in points])
max_x = max([x for (x, y, lat, lon, color) in points])
max_y = max([y for (x, y, lat, lon, color) in points])

print (min_x, min_y), (max_x, max_y)

top, left, bottom, right = 10, 10, img.size[1] - 10, img.size[0] - 10

mx = (right - left) / (max_x - min_x)
my = (bottom - top) / (max_y - min_y)

mx, my = min(mx, my), min(mx, my)

bx = left - mx * min_x
by = top - my * min_y

print 'Drawing points...'
for (x, y, lat, lon, color) in points:
    x, y = mx * x + bx, my * y + by
    draw.rectangle((x-3, y-3, x, y), fill=color)

img.save('out.png')