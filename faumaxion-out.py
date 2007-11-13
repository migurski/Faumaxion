import sys, gzip, re, random, math, cPickle, operator
import gnomonic, icosahedron, mesh, transform
import PIL.Image as Image
from PIL.ImageDraw import ImageDraw

print 'Laying out faces...'
lat, lon = map(float, sys.argv[-2:])
face = icosahedron.vertex2face(icosahedron.latlon2vertex(lat, lon))

face.orient_north(lat, lon)
faces = face.arrange_neighbors()

points = []
img = Image.new('RGB', (600, 600), 0x00)
draw = ImageDraw(img)

print 'Loading colors...'
colors = cPickle.load(gzip.open('world.topo.bathy-colors.pickle.gz'))

print 'Projecting points...'
for lat in range(-90, 90, 3):
    for lon in range(-180, 180, 3):
        try:
            r, g, b = colors[lat, lon]
        except KeyError:
            continue

        face = icosahedron.vertex2face(icosahedron.latlon2vertex(lat, lon))
        x, y = face.project_latlon(lat, lon)
        
        points.append((x, y, lat, lon, (r, g, b)))

min_x = min([x for (x, y, lat, lon, color) in points])
min_y = min([y for (x, y, lat, lon, color) in points])
max_x = max([x for (x, y, lat, lon, color) in points])
max_y = max([y for (x, y, lat, lon, color) in points])

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

print 'Drawing lines...'
for face in faces:
    for edge in face.edges():
        x, y = face.project_vertex(edge.vertexA)
        x1, y1 = mx * x + bx, my * y + by
        
        x, y = face.project_vertex(edge.vertexB)
        x2, y2 = mx * x + bx, my * y + by
        
        if edge.kind == icosahedron.LAND:
            draw.line((x1, y1, x2, y2), fill=(0x00, 0xCC, 0x00))
        elif edge.kind == icosahedron.WATER:
            draw.line((x1, y1, x2, y2), fill=(0x00, 0x66, 0xFF))

img.save('out.png')